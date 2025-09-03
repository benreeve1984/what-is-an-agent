"""Tool implementations for the agent."""
import os
import json
import pandas as pd
import numpy as np
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, Optional


def list_data_files(folder: str = "data") -> Dict:
    """List all CSV files in the specified folder."""
    files = []
    folder_path = Path(folder)
    
    if not folder_path.exists():
        return {"error": f"Folder '{folder}' not found"}
    
    for file_path in folder_path.glob("*.csv"):
        size_kb = file_path.stat().st_size / 1024
        files.append({
            "name": file_path.name,
            "size_kb": round(size_kb, 1),
            "path": str(file_path)
        })
    
    return {
        "folder": folder,
        "csv_files": files,
        "count": len(files)
    }


def load_csv_factory(tables: Dict[str, pd.DataFrame]):
    """Factory to create load_csv function with access to tables."""
    def load_csv(path: str, name: str) -> Dict:
        """Load a CSV file into memory as a table."""
        try:
            df = pd.read_csv(path)
            tables[name] = df
            
            # Save to workings folder for inspection
            os.makedirs("workings", exist_ok=True)
            df.to_csv(f"workings/{name}_loaded.csv", index=False)
            
            return {
                "loaded_rows": len(df),
                "columns": list(df.columns),
                "table_name": name,
                "sample": df.head(3).to_dict('records')
            }
        except Exception as e:
            return {"error": str(e)}
    return load_csv


def examine_table_factory(tables: Dict[str, pd.DataFrame]):
    """Factory to create examine_table function with access to tables."""
    def examine_table(name: str) -> Dict:
        """Examine a loaded table's structure and content."""
        if name not in tables:
            return {"error": f"Table '{name}' not found"}
        
        df = tables[name]
        schema = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Infer semantic type
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if 'datetime' in dtype or (isinstance(sample, str) and 'T' in str(sample)):
                semantic_type = 'timestamp'
            elif pd.api.types.is_numeric_dtype(df[col]):
                semantic_type = 'numeric'
            else:
                semantic_type = 'categorical'
            
            schema[col] = {
                "dtype": dtype,
                "semantic_type": semantic_type,
                "non_null": int(df[col].notna().sum()),
                "unique_values": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(5).tolist()
            }
        
        return {
            "table": name,
            "rows": len(df),
            "columns": len(df.columns),
            "schema": schema
        }
    return examine_table


def sql_query_factory(tables: Dict[str, pd.DataFrame]):
    """Factory to create sql_query function with access to tables."""
    def sql_query(query: str, save_as: Optional[str] = None) -> Dict:
        """Execute SQL queries using DuckDB."""
        try:
            conn = duckdb.connect(':memory:')
            
            # Register all tables
            for table_name, df in tables.items():
                conn.register(table_name, df)
            
            # Execute query
            result_df = conn.execute(query).fetchdf()
            
            # Save result if requested
            if save_as:
                tables[save_as] = result_df
                # Also save to file
                os.makedirs("workings", exist_ok=True)
                result_df.to_csv(f"workings/{save_as}.csv", index=False)
            
            conn.close()
            
            return {
                "rows": len(result_df),
                "columns": list(result_df.columns),
                "saved_as": save_as,
                "result": result_df.head(10).to_dict('records')
            }
        except Exception as e:
            return {"error": str(e)}
    return sql_query


def analyze_statistics_factory(tables: Dict[str, pd.DataFrame]):
    """Factory to create analyze_statistics function with access to tables."""
    def analyze_statistics(table: str, column: str, group_by: Optional[str] = None) -> Dict:
        """Compute statistical summaries."""
        if table not in tables:
            return {"error": f"Table '{table}' not found"}
        
        df = tables[table]
        
        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}
        
        if group_by and group_by in df.columns:
            # Grouped statistics
            stats = df.groupby(group_by)[column].agg([
                'count', 'mean', 'std', 'min', 'max'
            ]).round(2).to_dict('index')
        else:
            # Overall statistics
            stats = {
                "count": int(df[column].count()),
                "mean": float(df[column].mean()),
                "std": float(df[column].std()),
                "min": float(df[column].min()),
                "max": float(df[column].max()),
                "q25": float(df[column].quantile(0.25)),
                "median": float(df[column].quantile(0.5)),
                "q75": float(df[column].quantile(0.75))
            }
        
        return {
            "table": table,
            "column": column,
            "group_by": group_by,
            "statistics": stats
        }
    return analyze_statistics


def create_chart_factory(tables: Dict[str, pd.DataFrame]):
    """Factory to create create_chart function with access to tables."""
    def create_chart(
        chart_type: str,
        table: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        color: Optional[str] = None
    ) -> str:
        """Create various types of charts using matplotlib."""
        if table not in tables:
            return f"Error: Table '{table}' not found"
        
        df = tables[table]
        
        plt.figure(figsize=(12, 7))
        
        try:
            if chart_type == "bar":
                if color and color in df.columns:
                    for group in df[color].unique():
                        subset = df[df[color] == group]
                        plt.bar(subset[x], subset[y], label=group, alpha=0.8)
                    plt.legend()
                else:
                    plt.bar(df[x], df[y], color='steelblue', alpha=0.8)
            
            elif chart_type == "line":
                if color and color in df.columns:
                    for group in df[color].unique():
                        subset = df[df[color] == group]
                        plt.plot(subset[x], subset[y], marker='o', label=group, linewidth=2)
                    plt.legend()
                else:
                    plt.plot(df[x], df[y], marker='o', color='darkblue', linewidth=2)
            
            elif chart_type == "scatter":
                if color and color in df.columns:
                    for group in df[color].unique():
                        subset = df[df[color] == group]
                        plt.scatter(subset[x], subset[y], label=group, alpha=0.7, s=50)
                    plt.legend()
                else:
                    plt.scatter(df[x], df[y], alpha=0.7, s=50, color='navy')
            
            elif chart_type == "histogram":
                plt.hist(df[x] if x else df[y], bins=30, alpha=0.7, color='teal', edgecolor='black')
            
            else:
                return f"Error: Unknown chart type '{chart_type}'"
            
            plt.title(title or f"{chart_type.title()} Chart", fontsize=14, fontweight='bold')
            plt.xlabel(xlabel or x, fontsize=12)
            plt.ylabel(ylabel or y, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save the figure
            os.makedirs("workings", exist_ok=True)
            filename = f"workings/{title.replace(' ', '_').lower()}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()  # Close instead of show for non-interactive
            
            return f"Chart created and saved as {filename}"
            
        except Exception as e:
            return f"Error creating chart: {str(e)}"
    return create_chart