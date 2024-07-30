
document.addEventListener("DOMContentLoaded", function(){
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
          document.getElementById('navbar_top').classList.add('fixed-top');
          // add padding top to show content behind navbar
          navbar_height = document.querySelector('.navbar').offsetHeight;
          document.body.style.paddingTop = navbar_height + 'px';
        } else {
          document.getElementById('navbar_top').classList.remove('fixed-top');
           // remove padding top from body
          document.body.style.paddingTop = '0';
        } 
    });
  }); 

function deselectAll() {
    // Get all checkboxes
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    // Loop through the checkboxes and uncheck them
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
    });
}

function isEmpty(p1) {
    
    if (p1.length > 0) {
        return false;
    }
    else if (p1.length === 0) {
        return true;
}
}


document.getElementById('plot-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Getting form data from from html form
    const selectedFunctions = Array.from(document.querySelectorAll('input[name="function"]:checked'))
                                   .map(input => input.value);
    const xRange = document.getElementById('x-axis').value;
    console.log(xRange);
    const fdate = document.getElementById('fdate').value; // For date inputs
    const tdate = document.getElementById('todate').value;
    const ddate = document.getElementById('ddates').value;

    // Validate form data and update alert messages
    if ( (isEmpty(ddate)) ) {  // Alert for date inputs
        if (isEmpty(fdate) || isEmpty(tdate)) {
            alert('Please select either a date range or a discreet date.');
            return;
        }
    }

    if (isEmpty(selectedFunctions)) { // Alert for parameters
        alert('Please select at least one parameter.');
        return;
    }



    fetch('/plot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        
        body: JSON.stringify({
            functions: selectedFunctions,
            x_range: xRange,
            fdate: fdate,  // Include the date in the POST request payload
            tdate: tdate,  // Include the  to date in the POST request payload
            ddate: ddate  // Include the discreet date in the POST request payload
        }    
    )
    })
    .then(response => response.json())
    .then(data => {
        
        // Getting values from the backend and creating traces for Plotly
        const traces = [];
        for (const [func, yValues] of Object.entries(data.y)) { //Defining Traces for Plotly
            traces.push({
                x: data.x,
                y: yValues,
                //mode: 'line',
                mode:'lines+markers',
                //type:"scatter",
                name: func
            });
        console.log(traces);
        }

        // Define Layout
        const layout = {
            margin: {
                l: 80,
                r: 50,
                b: 50,
                t: 50,
                pad: 4
            },
            plot_bgcolor:"#fbfbfb",
            paper_bgcolor:"#fbfbfb",
            showlegend: true,
            //title: "ILMT",
            xaxis: {
                automargin: true,
                tickangle: 40,
                title: {
                    text: data.xlabel,
                    standoff: 20
                }
            }
            
        };
        
        Plotly.newPlot('plot', traces, layout);
    });
});


