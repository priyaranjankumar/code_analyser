"""
Flowchart generator using D3.js for program visualization
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Template


class FlowchartGenerator:
    """Generates interactive flowcharts using D3.js and LLM analysis"""
    
    def __init__(self, output_dir: Path, llm_client=None):
        """
        Initialize flowchart generator
        
        Args:
            output_dir: Output directory for flowchart files
            llm_client: LLM client for generating flowchart descriptions
        """
        self.output_dir = Path(output_dir)
        self.flowchart_dir = self.output_dir / 'flowcharts'
        self.flowchart_dir.mkdir(parents=True, exist_ok=True)
        self.llm_client = llm_client
        
        # Load D3.js template
        self.template = self._load_template()
    
    def _load_template(self) -> Template:
        """Load D3.js flowchart template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ program_name }} - Flowchart</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }
        .flow-description {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }
        .flow-description h3 {
            margin-top: 0;
            color: #495057;
        }
        .flow-description p {
            margin: 10px 0;
            line-height: 1.6;
        }
        .flowchart-container {
            width: 100%;
            height: 700px;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
            background: #fafafa;
        }
        .node {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .node:hover {
            filter: brightness(1.1);
        }
        .node-text {
            font-size: 11px;
            font-weight: bold;
            text-anchor: middle;
            dominant-baseline: middle;
            fill: white;
            pointer-events: none;
        }
        .node-description {
            font-size: 10px;
            fill: #333;
            text-anchor: middle;
            dominant-baseline: middle;
            pointer-events: none;
        }
        .link {
            stroke: #666;
            stroke-width: 2;
            fill: none;
            marker-end: url(#arrowhead);
        }
        .link-label {
            font-size: 10px;
            fill: #666;
            text-anchor: middle;
            dominant-baseline: middle;
            pointer-events: none;
        }
        .controls {
            margin: 20px 0;
            text-align: center;
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .zoom-info {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
        }
        .fullscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 9999;
            background: white;
        }
        .fullscreen .container {
            max-width: none;
            height: 100vh;
            margin: 0;
            border-radius: 0;
        }
        .fullscreen .flowchart-container {
            height: calc(100vh - 200px);
        }
        .fullscreen .controls {
            position: sticky;
            top: 0;
            background: white;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
            z-index: 1000;
        }
        .legend {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .legend h4 {
            margin-top: 0;
            color: #495057;
        }
        .legend-item {
            display: inline-block;
            margin: 5px 15px 5px 0;
            font-size: 12px;
        }
        .legend-color {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 5px;
            vertical-align: middle;
        }
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ program_name }}</h1>
            <p>Program Flowchart - Interactive Visualization</p>
        </div>
        
        {% if flow_description %}
        <div class="flow-description">
            <h3>Program Flow Overview</h3>
            <p><strong>Main Flow:</strong> {{ flow_description.main_flow }}</p>
            {% if flow_description.decision_points %}
            <p><strong>Key Decision Points:</strong> {{ flow_description.decision_points }}</p>
            {% endif %}
            {% if flow_description.loops %}
            <p><strong>Loops and Iterations:</strong> {{ flow_description.loops }}</p>
            {% endif %}
            {% if flow_description.error_handling %}
            <p><strong>Error Handling:</strong> {{ flow_description.error_handling }}</p>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="legend">
            <h4>Node Types</h4>
            <div class="legend-item">
                <span class="legend-color" style="background: #28a745;"></span>
                <span>Start/End</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #007bff;"></span>
                <span>Process</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ffc107;"></span>
                <span>Decision</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fd7e14;"></span>
                <span>Input/Output</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #6f42c1;"></span>
                <span>Procedure Call</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #20c997;"></span>
                <span>Loop</span>
            </div>
        </div>
        
        <div class="legend">
            <h4>Interactive Controls</h4>
            <div style="font-size: 12px; color: #666; line-height: 1.6;">
                <strong>Mouse:</strong> Drag to pan, Scroll wheel to zoom<br>
                <strong>Keyboard:</strong> +/= (zoom in), - (zoom out), 0 (reset), F (fit to screen), Esc (exit fullscreen)<br>
                <strong>Hover:</strong> Over nodes to see detailed information
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-secondary" onclick="zoomIn()">🔍 Zoom In</button>
            <button class="btn btn-secondary" onclick="zoomOut()">🔍 Zoom Out</button>
            <button class="btn btn-secondary" onclick="resetZoom()">🔄 Reset</button>
            <button class="btn btn-success" onclick="fitToScreen()">📐 Fit to Screen</button>
            <button class="btn" onclick="toggleFullscreen()">⛶ Fullscreen</button>
            <button class="btn btn-secondary" onclick="downloadSVG()">💾 Download SVG</button>
        </div>
        
        <div class="zoom-info" id="zoomInfo" style="display: none;">
            Zoom: <span id="zoomLevel">100%</span>
        </div>
        
        <div class="flowchart-container" id="flowchart"></div>
    </div>
    
    <div class="tooltip" id="tooltip" style="display: none;"></div>
    
    <script>
        // Flowchart data
        const flowchartData = {{ flowchart_data | safe }};
        
        // Global variables for zoom and fullscreen
        let currentZoom = 1;
        let isFullscreen = false;
        
        // Set up SVG
        const container = document.getElementById('flowchart');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        const svg = d3.select('#flowchart')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Create a group for zooming
        const g = svg.append('g');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 5])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
                currentZoom = event.transform.k;
                updateZoomInfo();
            });
        
        svg.call(zoom);
        
        // Mouse wheel zoom
        svg.on('wheel', (event) => {
            event.preventDefault();
            const zoomLevel = event.deltaY > 0 ? 0.9 : 1.1;
            const newZoom = currentZoom * zoomLevel;
            
            if (newZoom >= 0.1 && newZoom <= 5) {
                const transform = d3.zoomTransform(svg.node());
                const newTransform = transform.scale(newZoom);
                svg.transition().duration(200).call(zoom.transform, newTransform);
            }
        });
        
        // Add arrow marker
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#666');
        
        // Create force simulation
        const simulation = d3.forceSimulation(flowchartData.nodes)
            .force('link', d3.forceLink(flowchartData.links).id(d => d.id).distance(120))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(40));
        
        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(flowchartData.links)
            .enter().append('line')
            .attr('class', 'link');
        
        // Create link labels
        const linkLabel = g.append('g')
            .selectAll('text')
            .data(flowchartData.links)
            .enter().append('text')
            .attr('class', 'link-label')
            .text(d => d.label || '');
        
        // Create nodes
        const node = g.append('g')
            .selectAll('g')
            .data(flowchartData.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Add node circles
        node.append('circle')
            .attr('r', d => d.type === 'DECISION' ? 25 : 20)
            .attr('fill', d => getNodeColor(d.type));
        
        // Add node labels
        node.append('text')
            .attr('class', 'node-text')
            .attr('dy', d => d.type === 'DECISION' ? 0 : 0)
            .text(d => d.label);
        
        // Add node descriptions (smaller text below)
        node.append('text')
            .attr('class', 'node-description')
            .attr('dy', d => d.type === 'DECISION' ? 35 : 30)
            .text(d => d.description ? d.description.substring(0, 15) + '...' : '');
        
        // Add tooltip
        node.on('mouseover', function(event, d) {
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `
                <strong>${d.label}</strong><br>
                ${d.description || ''}<br>
                ${d.business_logic ? '<br><strong>Business Logic:</strong> ' + d.business_logic : ''}
                ${d.line_number ? '<br><strong>Line:</strong> ' + d.line_number : ''}
            `;
            tooltip.style.display = 'block';
            tooltip.style.left = event.pageX + 10 + 'px';
            tooltip.style.top = event.pageY - 10 + 'px';
        })
        .on('mouseout', function() {
            document.getElementById('tooltip').style.display = 'none';
        });
        
        // Update positions on simulation tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            linkLabel
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
            
            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Utility functions
        function getNodeColor(type) {
            const colors = {
                'START': '#28a745',
                'END': '#28a745',
                'PROCESS': '#007bff',
                'DECISION': '#ffc107',
                'IO': '#fd7e14',
                'CALL': '#6f42c1',
                'LOOP': '#20c997'
            };
            return colors[type] || '#6c757d';
        }
        
        function updateZoomInfo() {
            const zoomInfo = document.getElementById('zoomInfo');
            const zoomLevel = document.getElementById('zoomLevel');
            if (zoomInfo && zoomLevel) {
                zoomLevel.textContent = Math.round(currentZoom * 100) + '%';
                zoomInfo.style.display = currentZoom !== 1 ? 'block' : 'none';
            }
        }
        
        function zoomIn() {
            const newZoom = Math.min(currentZoom * 1.2, 5);
            const transform = d3.zoomTransform(svg.node());
            const newTransform = transform.scale(newZoom);
            svg.transition().duration(300).call(zoom.transform, newTransform);
        }
        
        function zoomOut() {
            const newZoom = Math.max(currentZoom / 1.2, 0.1);
            const transform = d3.zoomTransform(svg.node());
            const newTransform = transform.scale(newZoom);
            svg.transition().duration(300).call(zoom.transform, newTransform);
        }
        
        function resetZoom() {
            svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
            simulation.alpha(1).restart();
        }
        
        function fitToScreen() {
            // Get the bounds of all nodes
            const nodes = flowchartData.nodes;
            if (nodes.length === 0) return;
            
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            
            nodes.forEach(node => {
                if (node.x !== undefined && node.y !== undefined) {
                    minX = Math.min(minX, node.x);
                    minY = Math.min(minY, node.y);
                    maxX = Math.max(maxX, node.x);
                    maxY = Math.max(maxY, node.y);
                }
            });
            
            // Add padding
            const padding = 50;
            minX -= padding;
            minY -= padding;
            maxX += padding;
            maxY += padding;
            
            // Calculate scale and translation
            const graphWidth = maxX - minX;
            const graphHeight = maxY - minY;
            const scale = Math.min(width / graphWidth, height / graphHeight) * 0.8;
            
            const transform = d3.zoomIdentity
                .translate(width / 2 - (minX + graphWidth / 2) * scale, 
                          height / 2 - (minY + graphHeight / 2) * scale)
                .scale(scale);
            
            svg.transition().duration(500).call(zoom.transform, transform);
        }
        
        function toggleFullscreen() {
            const container = document.querySelector('.container');
            const flowchartContainer = document.getElementById('flowchart');
            
            if (!isFullscreen) {
                // Enter fullscreen
                container.classList.add('fullscreen');
                isFullscreen = true;
                
                // Update SVG size
                const newWidth = window.innerWidth;
                const newHeight = window.innerHeight - 200;
                svg.attr('width', newWidth).attr('height', newHeight);
                
                // Update simulation center
                simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
                simulation.alpha(1).restart();
                
                // Update button text
                event.target.textContent = '⛶ Exit Fullscreen';
            } else {
                // Exit fullscreen
                container.classList.remove('fullscreen');
                isFullscreen = false;
                
                // Restore original size
                const originalWidth = container.clientWidth;
                const originalHeight = 700;
                svg.attr('width', originalWidth).attr('height', originalHeight);
                
                // Update simulation center
                simulation.force('center', d3.forceCenter(originalWidth / 2, originalHeight / 2));
                simulation.alpha(1).restart();
                
                // Update button text
                event.target.textContent = '⛶ Fullscreen';
            }
        }
        
        function downloadSVG() {
            const svgElement = document.querySelector('#flowchart svg');
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const svgUrl = URL.createObjectURL(svgBlob);
            const downloadLink = document.createElement('a');
            downloadLink.href = svgUrl;
            downloadLink.download = '{{ program_name }}_flowchart.svg';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.key === '+' || event.key === '=') {
                event.preventDefault();
                zoomIn();
            } else if (event.key === '-') {
                event.preventDefault();
                zoomOut();
            } else if (event.key === '0') {
                event.preventDefault();
                resetZoom();
            } else if (event.key === 'f') {
                event.preventDefault();
                fitToScreen();
            } else if (event.key === 'Escape' && isFullscreen) {
                toggleFullscreen();
            }
        });
    </script>
</body>
</html>
        """
        return Template(template_content)
    
    def generate_flowchart(self, program_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate flowchart for a program using LLM analysis
        
        Args:
            program_data: Program data with AST and LLM analysis
            
        Returns:
            Path to generated flowchart HTML file
        """
        try:
            program_name = program_data.get('name', 'Unknown')
            ast_data = program_data.get('ast', {})  # Changed from 'ast_data' to 'ast'
            
            print(f"  Generating flowchart for {program_name}...")
            
            # Get LLM-generated flowchart description
            flowchart_description = self._get_llm_flowchart_description(program_data)
            
            # Generate flowchart data from LLM description
            flowchart_data = self._generate_flowchart_data_from_llm(flowchart_description, ast_data)
            
            # Prepare template variables
            template_vars = {
                'program_name': program_name,
                'flow_description': flowchart_description,
                'flowchart_data': json.dumps(flowchart_data)
            }
            
            # Generate HTML file
            filename = f"{program_name}_flowchart.html"
            file_path = self.flowchart_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.template.render(**template_vars))
            
            print(f"  ✓ Flowchart generated: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"Error generating flowchart for {program_data.get('name', 'Unknown')}: {e}")
            return None
    
    def _get_llm_flowchart_description(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get flowchart description from LLM
        
        Args:
            program_data: Program data
            
        Returns:
            LLM-generated flowchart description
        """
        if not self.llm_client:
            # Fallback to mock data if no LLM client
            return self._generate_mock_flowchart_description(program_data)
        
        try:
            # Get LLM description
            llm_response = self.llm_client.generate_flowchart_description(program_data)
            
            # Try to parse JSON from LLM response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, create structured description
            return {
                'flow_description': llm_response,
                'main_flow': 'Program flow analysis from LLM',
                'decision_points': 'Key decision points identified',
                'loops': 'Loop structures found',
                'error_handling': 'Error handling mechanisms'
            }
            
        except Exception as e:
            print(f"  Warning: LLM flowchart generation failed: {e}")
            return self._generate_mock_flowchart_description(program_data)
    
    def _generate_mock_flowchart_description(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock flowchart description for testing"""
        name = program_data.get('name', 'Unknown')
        statements = program_data.get('statements', [])
        
        return {
            'flow_description': f'Mock flowchart description for {name}',
            'main_flow': f'Program {name} processes data through {len(statements)} statements',
            'decision_points': 'IF statements for data validation and business logic',
            'loops': 'PERFORM statements for data processing loops',
            'error_handling': 'Basic error handling through IF conditions'
        }
    
    def _generate_flowchart_data_from_llm(self, flowchart_description: Dict[str, Any], ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate flowchart data from LLM description
        
        Args:
            flowchart_description: LLM-generated flowchart description
            ast_data: Program AST data
            
        Returns:
            Dictionary with nodes and links for D3.js
        """
        nodes = []
        links = []
        node_id = 0
        
        # If LLM provided structured data, use it
        if 'nodes' in flowchart_description and 'connections' in flowchart_description:
            return self._process_llm_structured_data(flowchart_description)
        
        # Otherwise, generate from AST with LLM guidance
        return self._generate_flowchart_from_ast_with_llm_guidance(flowchart_description, ast_data)
    
    def _process_llm_structured_data(self, flowchart_description: Dict[str, Any]) -> Dict[str, Any]:
        """Process LLM-provided structured flowchart data"""
        nodes = []
        links = []
        
        # Process nodes
        for node_data in flowchart_description.get('nodes', []):
            node = {
                'id': node_data.get('id', f'node_{len(nodes)}'),
                'label': node_data.get('label', 'Unknown'),
                'type': node_data.get('type', 'PROCESS'),
                'description': node_data.get('description', ''),
                'business_logic': node_data.get('business_logic', ''),
                'line_number': node_data.get('line_number', 0)
            }
            nodes.append(node)
        
        # Process connections
        for conn_data in flowchart_description.get('connections', []):
            link = {
                'source': conn_data.get('from', ''),
                'target': conn_data.get('to', ''),
                'label': conn_data.get('label', ''),
                'type': conn_data.get('type', 'NORMAL')
            }
            links.append(link)
        
        return {'nodes': nodes, 'links': links}
    
    def _generate_flowchart_from_ast_with_llm_guidance(self, flowchart_description: Dict[str, Any], ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate flowchart from AST with LLM guidance
        
        Args:
            flowchart_description: LLM description for guidance
            ast_data: Program AST data
            
        Returns:
            Dictionary with nodes and links for D3.js
        """
        nodes = []
        links = []
        node_id = 0
        
        statements = ast_data.get('statements', [])
        procedures = ast_data.get('procedures', [])
        
        # Add start node
        start_node = {
            'id': f'node_{node_id}',
            'label': 'START',
            'type': 'START',
            'description': 'Program initialization',
            'business_logic': 'Program entry point',
            'line_number': 1
        }
        nodes.append(start_node)
        start_id = start_node['id']
        node_id += 1
        
        current_node = start_id
        
        # Track procedure entry points
        procedure_starts = {proc.get('start_line', 0): proc.get('name', '') for proc in procedures}
        
        # Create nodes for major flow control statements with LLM guidance
        major_statements = []
        
        for i, statement in enumerate(statements):
            stmt_type = statement.get('type', 'STATEMENT')
            line = statement.get('line', 0)
            content = statement.get('content', '')
            
            # Check if this is a procedure entry point
            if line in procedure_starts:
                major_statements.append({
                    'type': 'CALL',
                    'content': f"PROCEDURE {procedure_starts[line]}",
                    'line': line,
                    'original': statement,
                    'business_logic': f'Call procedure {procedure_starts[line]}'
                })
                continue
            
            # Include major flow control statements with business context
            if stmt_type in ['PERFORM', 'CALL', 'IF', 'ELSE', 'END-IF', 'OPEN', 'CLOSE', 'STOP', 'DISPLAY', 'ACCEPT', 'READ', 'WRITE', 'EVALUATE', 'WHEN', 'MOVE']:
                business_logic = self._get_business_logic(stmt_type, statement, flowchart_description)
                major_statements.append({
                    'type': stmt_type,
                    'content': content,
                    'line': line,
                    'original': statement,
                    'business_logic': business_logic
                })
        
        # If no major statements found, include some basic statements to show flow
        if len(major_statements) == 0:
            for i, statement in enumerate(statements[:10]):  # Limit to first 10
                stmt_type = statement.get('type', 'STATEMENT')
                content = statement.get('content', '')
                line = statement.get('line', 0)
                
                if stmt_type != 'STATEMENT' or 'PIC' in content or 'VALUE' in content:
                    continue  # Skip variable declarations
                
                major_statements.append({
                    'type': stmt_type,
                    'content': content,
                    'line': line,
                    'original': statement,
                    'business_logic': 'Process statement'
                })
        
        # Create nodes for major statements
        for stmt_info in major_statements:
            stmt_type = stmt_info['type']
            content = stmt_info['content']
            business_logic = stmt_info['business_logic']
            
            # Create node for this major statement
            node = {
                'id': f'node_{node_id}',
                'label': self._get_node_label(stmt_type, content),
                'type': self._get_node_type(stmt_type),
                'description': content[:50] + '...' if len(content) > 50 else content,
                'business_logic': business_logic,
                'line_number': stmt_info['line']
            }
            nodes.append(node)
            
            # Create link from previous node
            links.append({
                'source': current_node,
                'target': node['id'],
                'label': '',
                'type': 'NORMAL'
            })
            
            current_node = node['id']
            node_id += 1
            
            # Handle special flow control
            if stmt_type == 'IF':
                # Add decision branch
                decision_node = {
                    'id': f'node_{node_id}',
                    'label': 'Decision',
                    'type': 'DECISION',
                    'description': f"IF: {stmt_info['original'].get('condition', '')}",
                    'business_logic': 'Business logic decision point',
                    'line_number': stmt_info['line']
                }
                nodes.append(decision_node)
                
                links.append({
                    'source': current_node,
                    'target': decision_node['id'],
                    'label': 'True',
                    'type': 'CONDITION_TRUE'
                })
                
                current_node = decision_node['id']
                node_id += 1
            elif stmt_type == 'EVALUATE':
                # Add decision branch for EVALUATE
                decision_node = {
                    'id': f'node_{node_id}',
                    'label': 'Evaluate',
                    'type': 'DECISION',
                    'description': f"EVALUATE: {content}",
                    'business_logic': 'Multi-condition decision point',
                    'line_number': stmt_info['line']
                }
                nodes.append(decision_node)
                
                links.append({
                    'source': current_node,
                    'target': decision_node['id'],
                    'label': 'Check',
                    'type': 'NORMAL'
                })
                
                current_node = decision_node['id']
                node_id += 1
        
        # Add end node
        end_node = {
            'id': f'node_{node_id}',
            'label': 'END',
            'type': 'END',
            'description': 'Program completion',
            'business_logic': 'Program termination',
            'line_number': len(statements) + 1
        }
        nodes.append(end_node)
        
        links.append({
            'source': current_node,
            'target': end_node['id'],
            'label': '',
            'type': 'NORMAL'
        })
        
        return {'nodes': nodes, 'links': links}
    
    def _get_business_logic(self, stmt_type: str, statement: Dict[str, Any], flowchart_description: Dict[str, Any]) -> str:
        """Get business logic description for a statement"""
        content = statement.get('content', '')
        
        business_logic_map = {
            'DISPLAY': 'Output data to user',
            'ACCEPT': 'Get input from user',
            'OPEN': 'Open file for processing',
            'CLOSE': 'Close file after processing',
            'READ': 'Read data from file',
            'WRITE': 'Write data to file',
            'PERFORM': 'Execute business logic procedure',
            'CALL': 'Call external program or procedure',
            'IF': 'Validate data or make business decision',
            'EVALUATE': 'Multi-condition decision logic',
            'WHEN': 'Condition branch',
            'MOVE': 'Assign data to variable',
            'STOP': 'Terminate program execution'
        }
        
        # Special handling for specific content
        if stmt_type == 'PERFORM' and 'SEND-MAP' in content:
            return 'Display login screen to user'
        elif stmt_type == 'PERFORM' and 'VALIDATION' in content:
            return 'Validate user credentials'
        elif stmt_type == 'EVALUATE' and 'EIBCALEN' in content:
            return 'Check if user data received'
        elif stmt_type == 'MOVE' and '-1' in content:
            return 'Initialize user ID field'
        
        return business_logic_map.get(stmt_type, 'Process data')
    
    def _get_node_label(self, stmt_type: str, content: str) -> str:
        """Get label for flowchart node"""
        if stmt_type == 'PROCEDURE':
            return 'PROCEDURE'
        elif stmt_type == 'IF':
            return 'IF'
        elif stmt_type == 'EVALUATE':
            return 'EVALUATE'
        elif stmt_type == 'WHEN':
            return 'WHEN'
        elif stmt_type == 'PERFORM':
            # Extract procedure name if available
            if 'PERFORM' in content:
                parts = content.split()
                if len(parts) > 1:
                    return parts[1][:10]  # First 10 chars of procedure name
            return 'PERFORM'
        elif stmt_type == 'CALL':
            return 'CALL'
        elif stmt_type == 'DISPLAY':
            return 'DISPLAY'
        elif stmt_type == 'ACCEPT':
            return 'ACCEPT'
        elif stmt_type == 'OPEN':
            return 'OPEN'
        elif stmt_type == 'CLOSE':
            return 'CLOSE'
        elif stmt_type == 'READ':
            return 'READ'
        elif stmt_type == 'WRITE':
            return 'WRITE'
        elif stmt_type == 'MOVE':
            return 'MOVE'
        elif stmt_type == 'STOP':
            return 'STOP'
        else:
            return stmt_type
    
    def _get_node_type(self, stmt_type: str) -> str:
        """Get node type for styling"""
        if stmt_type in ['START', 'END']:
            return 'START'
        elif stmt_type in ['IF', 'EVALUATE', 'WHEN']:
            return 'DECISION'
        elif stmt_type in ['DISPLAY', 'ACCEPT', 'OPEN', 'CLOSE', 'READ', 'WRITE']:
            return 'IO'
        elif stmt_type in ['PERFORM', 'CALL']:
            return 'CALL'
        elif stmt_type == 'MOVE':
            return 'PROCESS'
        else:
            return 'PROCESS' 