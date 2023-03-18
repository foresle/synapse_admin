const setMapFromJson = (graph_data) => {
    const graph = JSON.parse(graph_data)
    const container = document.getElementById('server_map')
    const nodes = new vis.DataSet(graph.nodes)
    const edges = new vis.DataSet(graph.edges)
    const data = {
        nodes: nodes,
        edges: edges
    }
    const network = new vis.Network(container, data, {});
}