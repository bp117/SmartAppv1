import os
import re
import networkx as nx

# Step 1: Parse SQL files and extract dependencies
def parse_sql_file(file_path):
    """
    Parse a single SQL file and extract CREATE/INSERT statements.
    Returns a dictionary of dependencies.
    """
    with open(file_path, 'r') as file:
        sql_content = file.read()

    # Regular expressions to identify CREATE/INSERT statements
    create_pattern = re.compile(r"CREATE\s+(?:TABLE|VIEW)\s+(\w+)", re.IGNORECASE)
    insert_pattern = re.compile(r"INSERT\s+INTO\s+(\w+)\s+SELECT.*FROM\s+(\w+)", re.IGNORECASE)
    select_pattern = re.compile(r"SELECT\s+.*\s+FROM\s+(\w+)", re.IGNORECASE)

    dependencies = []
    
    # Extract CREATE statements
    for match in create_pattern.finditer(sql_content):
        table_name = match.group(1)
        dependencies.append(('CREATE', table_name))

    # Extract INSERT INTO ... SELECT FROM statements
    for match in insert_pattern.finditer(sql_content):
        target_table = match.group(1)
        source_table = match.group(2)
        dependencies.append(('INSERT', target_table, source_table))

    # Extract SELECT statements
    for match in select_pattern.finditer(sql_content):
        source_table = match.group(1)
        dependencies.append(('SELECT', source_table))

    return dependencies


# Step 2: Build a dependency graph
def build_dependency_graph(directory):
    """
    Parse all SQL files in the directory and build a dependency graph.
    """
    graph = nx.DiGraph()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                dependencies = parse_sql_file(file_path)
                for dep in dependencies:
                    if dep[0] == 'CREATE':
                        graph.add_node(dep[1])  # Add table/view node
                    elif dep[0] == 'INSERT':
                        graph.add_edge(dep[2], dep[1])  # Source -> Target
                    elif dep[0] == 'SELECT':
                        graph.add_node(dep[1])  # Add source table node
    return graph


# Step 3: Find lineage using recursion
def find_column_lineage(graph, target_column, current_table, visited=None):
    """
    Recursively find the lineage of a column starting from a given table.
    """
    if visited is None:
        visited = set()

    if current_table in visited:
        return []  # Avoid cycles

    visited.add(current_table)
    lineage = []

    # Check predecessors (tables/views that populate this table)
    for predecessor in graph.predecessors(current_table):
        lineage.append((predecessor, current_table))
        lineage.extend(find_column_lineage(graph, target_column, predecessor, visited))

    return lineage


# Step 4: Main function to execute the lineage extraction
def main(directory, target_column, start_table):
    """
    Main function to extract column lineage.
    """
    # Build the dependency graph
    graph = build_dependency_graph(directory)

    # Find lineage starting from the specified table
    lineage = find_column_lineage(graph, target_column, start_table)

    print("Column Lineage:")
    for source, target in lineage:
        print(f"{source} -> {target}")


# Example usage
if __name__ == "__main__":
    sql_directory = "path/to/sql/files"
    target_column = "guarantor_nm"
    start_table = "final_output_table"  # Replace with the table where the column is used

    main(sql_directory, target_column, start_table)
