document.getElementById('plot-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const selectedFunctions = Array.from(document.querySelectorAll('input[name="function"]:checked'))
                                   .map(input => input.value);
    const xRange = document.getElementById('x-range').value;
    const date = document.getElementById('date').value; // For date inputs

    fetch('/plot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            functions: selectedFunctions,
            x_range: parseInt(xRange),
            date: date  // Include the date in the POST request payload
        })
    })
    .then(response => response.json())
    .then(data => {
        const traces = [];

        for (const [func, yValues] of Object.entries(data.y)) {
            traces.push({
                x: data.x,
                y: yValues,
                mode: 'lines',
                name: func
            });
        }

        Plotly.newPlot('plot', traces);
    });
});
