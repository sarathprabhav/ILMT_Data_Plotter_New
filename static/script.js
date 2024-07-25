document.getElementById('plot-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const selectedFunctions = Array.from(document.querySelectorAll('input[name="function"]:checked'))
                                   .map(input => input.value);
    const xRange = document.getElementById('x-range').value;
    const fdate = document.getElementById('fdate').value; // For date inputs
    const tdate = document.getElementById('todate').value;
    const ddate = document.getElementById('ddates').value;
    alert("I am an alert box!");
    fetch('/plot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            functions: selectedFunctions,
            x_range: parseInt(xRange),
            fdate: fdate,  // Include the date in the POST request payload
            tdate: tdate,  // Include the  to date in the POST request payload
            ddate: ddate  // Include the discreet date in the POST request payload
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
