import networkx as nx
import pandas as pd
import streamlit as st

# Load data and build graph
def load_data(filename, min_scenes=1):
    data = pd.read_csv(filename)
    G = nx.Graph()
    for _, row in data.iterrows():
        if row['Scenes Together'] >= min_scenes:  # Only keep strong connections
            G.add_edge(row['Character 1'], row['Character 2'], weight=row['Scenes Together'])
    return G

# Analysis functions
def top_connected_characters(graph, top_n=3):
    degrees = dict(graph.degree())
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    return sorted_degrees[:top_n]

def top_strongest_pairs(graph, top_n=3):
    edges = graph.edges(data=True)
    sorted_edges = sorted(edges, key=lambda x: x[2]['weight'], reverse=True)
    return [((u, v), data['weight']) for u, v, data in sorted_edges[:top_n]]

def shortest_path(graph, char1, char2):
    try:
        path = nx.shortest_path(graph, char1, char2)  # Correct call
        return path
    except nx.NetworkXNoPath:
        return None
    
def get_family(character):
    family_groups = {
        "Pritchett": ["Jay", "Gloria", "Manny", "Joe"],
        "Dunphy": ["Claire", "Phil", "Haley", "Alex", "Luke"],
        "Tucker-Pritchett": ["Mitchell", "Cameron", "Lily"]
    }
    for family, members in family_groups.items():
        if character in members:
            return family
    return "Unknown"

def character_stats(graph, character):
    stats = {}
    stats['total_scenes'] = sum(data['weight'] for _, _, data in graph.edges(character, data=True))
    neighbors = graph[character]
    stats['top_co_character'] = max(neighbors.items(), key=lambda x: x[1]['weight'])
    stats['unique_co_appearances'] = len(neighbors)
    stats['family'] = get_family(character)
    return stats


# Streamlit UI
def main():
    st.set_page_config(page_title="Modern Family Analysis", layout="wide")
    st.title("📺 Modern Family Character Interaction Analysis")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🔧 Settings")
        min_scenes = st.selectbox(
            "Minimum Scenes Shared to Show a Connection:",
            options=[1, 10, 30, 50, 100],
            index=3,  # Default to 50
            help="Only show character connections where they appeared together at least this many times. Higher values will hide weaker relationships."
        )
        
        st.markdown("---")
        st.header("📖 About This App")
        st.info(
            "Analyze relationships between Modern Family characters:\n"
            "- Find the most connected characters\n"
            "- Discover the strongest character pairs\n"
            "- Trace relationship paths\n"
            "- Explore detailed character stats"
        )
    
    # Load data with current filter
    G = load_data('coappearance_list.csv', min_scenes)
    nodes = sorted(G.nodes())
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔗 Most Connected", 
        "💪 Strongest Pairs", 
        "🛣️ Path Finder", 
        "📊 Character Stats"
    ])

    with tab1:
        st.header("Top Connected Characters")
        st.caption("Characters with the most interactions (connections).")
        
        top_n = st.number_input(
            "How many top characters to show:",
            min_value=1, max_value=20, value=5, key="top_connected_num"
        )
        top_chars = top_connected_characters(G, top_n)

        for idx, (char, degree) in enumerate(top_chars, 1):
            st.write(f"**{idx}. {char}** — {degree} connections")

    with tab2:
        st.header("Strongest Character Pairs")
        st.caption("Pairs who shared the most scenes together.")

        top_n = st.number_input(
            "How many top pairs to show:",
            min_value=1, max_value=20, value=5, key="top_pairs_num"
        )
        top_pairs = top_strongest_pairs(G, top_n)

        for idx, ((char1, char2), weight) in enumerate(top_pairs, 1):
            st.write(f"**{idx}. {char1} & {char2}** — {weight} scenes together")

    with tab3:
        st.header("Character Path Finder")
        st.caption("Find how two characters are connected through others.")

        char1 = st.selectbox("First Character", nodes, key="path_char1")
        char2 = st.selectbox(
            "Second Character", 
            [c for c in nodes if c != char1], 
            key="path_char2"
        )

        if st.button("Find Path", use_container_width=True):
            if char1 == char2:
                st.warning("Please select two different characters.")
            else:
                path = shortest_path(G, char1, char2)
                if path:
                    st.success(f"Connection Path: {' → '.join(path)}")
                else:
                    st.error("No connection path exists.")
 
    with tab4:
        st.header("Character Statistics")
        st.caption("Detailed information for each character.")

        char = st.selectbox("Select a Character", nodes, key="stats_char")

        if st.button("Show Character Stats", use_container_width=True):
            stats = character_stats(G, char)

            st.metric("Family Group", stats['family'])
            st.metric("Total Scenes Appeared", stats['total_scenes'])
            top_co_char, weight_info = stats['top_co_character']
            weight = weight_info['weight']
            st.metric("Top Co-Star", f"{top_co_char} ({weight} scenes)")
            st.metric("Number of Character Connections", stats['unique_co_appearances'])

if __name__ == "__main__":
    main()