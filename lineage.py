def get_column_lineage(sql_text, target_table, target_column):
    prompt = f"""
    You are an expert SQL lineage analyzer with deep expertise in complex SQL stored procedures. Your task is to extract the complete column lineage for a specific target column from a specific target table from the SQL code provided below. The stored procedures can include advanced SQL constructs such as:
    
    - Volatile or temporary tables, CTEs, and derived tables.
    - Multiple levels of table aliases and subquery nesting.
    - Indirect column derivations (e.g., columns transformed by functions, expressions, or CASE statements).
    - Complex join conditions and aggregations that transform data.
    - Mixed usage of explicit column naming and implicit column propagation.
    
    Instructions:
    1. Ignore all comments in the SQL code.
    2. Identify and locate the target table "{target_table}" and the target column "{target_column}".
    3. Trace the lineage of {target_column} by following every transformation step, including:
       - Direct mappings (e.g., SELECT source_column AS {target_column}).
       - Indirect mappings (e.g., SELECT UPPER(source_column), COALESCE(source_column, 'default')).
       - Alias resolution in subqueries, temporary tables, or CTEs.
       - Any intermediate transformations leading to the final derivation.
    4. For every mapping step, extract the following details:
       - target_table, target_column, source_db, source_table, source_column, mapping_logic.
    5. If the target column is not found, output exactly "COLUMN NOT FOUND IN THE SQL PROCEDURE."
    
    Final Output:
    Provide your result as CSV text with headers:
    target_table, target_column, source_db, source_table, source_column, mapping_logic
    
    SQL Content:
    {sql_text}
    """
    responses = call_gemini(prompt)
    return responses





import sqlparse
from networkx import DiGraph, draw, spring_layout
import matplotlib.pyplot as plt

# Function to parse SQL files and extract object definitions
def parse_sql_file(file_path):
    """
    Parse an SQL file and extract object definitions (procedures, views, etc.).
    Returns a dictionary mapping object names to their SQL definitions.
    """
    with open(file_path, 'r') as file:
        sql_content = file.read()

    # Use sqlparse to split the file into statements
    statements = sqlparse.split(sql_content)

    objects = {}
    for statement in statements:
        parsed = sqlparse.parse(statement)
        if not parsed:
            continue

        stmt = parsed[0]
        if stmt.get_type() in ['CREATE', 'REPLACE']:
            # Extract the object name
            obj_name = None
            for token in stmt.tokens:
                if token.ttype in sqlparse.tokens.Keyword and token.value.upper() in ['PROCEDURE', 'VIEW', 'FUNCTION']:
                    obj_name_token = stmt.token_next(stmt.token_index(token))
                    if isinstance(obj_name_token, tuple):
                        obj_name_token = obj_name_token[1]  # Extract the actual token
                    if obj_name_token and obj_name_token.ttype == sqlparse.tokens.Name:
                        obj_name = obj_name_token.value.strip()
                        break

            if obj_name:
                objects[obj_name] = statement.strip()

    return objects


# Function to extract dependencies from SQL definitions
def extract_dependencies(sql_definition):
    """
    Extract dependencies (tables, columns, procedures) from a SQL definition.
    Returns a list of dependent objects.
    """
    dependencies = set()

    # Parse the SQL statement
    parsed = sqlparse.parse(sql_definition)[0]

    # Traverse the parsed tokens to find table/column references
    for token in parsed.flatten():
        if token.ttype == sqlparse.tokens.Name and '.' in token.value:
            dependencies.add(token.value.strip())  # Add table.column format

        # Check for procedure calls
        if token.match(sqlparse.tokens.Keyword, ['CALL', 'EXEC']):
            proc_name_token = parsed.token_next(parsed.token_index(token))
            if isinstance(proc_name_token, tuple):
                proc_name_token = proc_name_token[1]
            if proc_name_token:
                dependencies.add(proc_name_token.value.strip())

        # Handle SELECT, INSERT, UPDATE statements
        if token.ttype == sqlparse.tokens.Keyword and token.value.upper() in ['SELECT', 'INSERT', 'UPDATE']:
            # Look for table references in the FROM clause or target table
            from_clause = parsed.token_next(parsed.token_index(token))
            while from_clause:
                if from_clause.ttype == sqlparse.tokens.Name:
                    dependencies.add(from_clause.value.strip())
                from_clause = parsed.token_next(parsed.token_index(from_clause))

    return list(dependencies)


# Recursive function to trace lineage
def trace_lineage(target_table, target_column, objects, visited=None, lineage=None, graph=None):
    """
    Recursively trace the lineage of a column in a target table.
    :param target_table: Name of the target table
    :param target_column: Name of the target column
    :param objects: Dictionary of parsed SQL objects
    :param visited: Set of visited objects to avoid infinite recursion
    :param lineage: List to store the lineage path
    :param graph: NetworkX graph to visualize dependencies
    :return: Lineage path as a list
    """
    if visited is None:
        visited = set()
    if lineage is None:
        lineage = []
    if graph is None:
        graph = DiGraph()

    key = f"{target_table}.{target_column}"
    if key in visited:
        return lineage  # Avoid infinite recursion

    visited.add(key)
    lineage.append(f"{target_table}.{target_column}")

    # Add node to the graph
    graph.add_node(f"{target_table}.{target_column}")

    # Search through all objects for references to the target table/column
    for obj_name, sql_definition in objects.items():
        dependencies = extract_dependencies(sql_definition)

        # Look for the target column in the dependencies
        for dependency in dependencies:
            dep_table, dep_column = dependency.split('.') if '.' in dependency else (dependency, None)

            if dep_table == target_table and (dep_column is None or dep_column == target_column):
                # Add edge to the graph
                graph.add_edge(f"{target_table}.{target_column}", f"{obj_name}.<definition>")

                # Recursively trace the lineage for the dependent object
                trace_lineage(dep_table, dep_column or target_column, objects, visited, lineage, graph)

    return lineage, graph


# Main function to execute lineage tracing
def main():
    # Parse SQL files
    file_paths = ['file1.sql', 'file2.sql']  # Replace with your SQL file paths
    all_objects = {}
    for file_path in file_paths:
        all_objects.update(parse_sql_file(file_path))

    # Define the target table and column
    target_table = "sales_summary"
    target_column = "total_sales"

    # Trace the lineage
    lineage, graph = trace_lineage(target_table, target_column, all_objects)

    # Print the lineage
    print("Lineage Path:")
    for step in lineage:
        print(step)

    # Visualize the lineage graph
    if graph.number_of_nodes() > 0:
        pos = spring_layout(graph)
        plt.figure(figsize=(10, 8))
        draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', font_size=10)
        plt.title("Lineage Graph")
        plt.show()


if __name__ == "__main__":
    main()
