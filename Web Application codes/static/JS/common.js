/* JavaScript for Gauge Chart */
$(function () {
  // Define a class for creating GaugeChart objects
  class GaugeChart {
    constructor(element, params) {
      this._element = element; // HTML element to render the gauge
      this._initialValue = params.initialValue; // Initial value for the gauge
      this._title = params.title; // Title of the gauge
      this._subtitle = params.subtitle; // Subtitle of the gauge
    }

    // Method to build the configuration object for the gauge
    _buildConfig() {
      let element = this._element;
      return {
        value: this._initialValue, // Initial value for the gauge
        valueIndicator: {
          color: "#aa5f2d", // Color for the value indicator
        },
        geometry: {
          startAngle: 180, // Start angle for the gauge
          endAngle: 360, // End angle for the gauge
        },
        scale: {
          startValue: 1000, // Start value for the scale
          endValue: 0, // End value for the scale
          customTicks: [0, 250, 500, 750, 1000], // Custom tick marks for the scale
          tick: {
            length: 8, // Length of the tick marks
          },
          label: {
            font: {
              color: "black", // Color for the scale labels
              size: 9, // Font size for the scale labels
              family: '"Open Sans", sans-serif', // Font family for the scale labels
            },
          },
        },
        title: {
          verticalAlignment: "bottom", // Vertical alignment of the title
          text: this._title, // Title text
          font: {
            family: '"Open Sans", sans-serif', // Font family for the title
            color: "black", // Color for the title
            size: 15, // Font size for the title
          },
          subtitle: {
            text: this._subtitle, // Subtitle text
            font: {
              family: '"Open Sans", sans-serif', // Font family for the subtitle
              color: "black", // Color for the subtitle
              weight: 700, // Font weight for the subtitle
              size: 32, // Font size for the subtitle
            },
          },
        },
        // Callback function to customize the gauge after initialization
        onInitialized: function () {
          let currentGauge = $(element);
          let circle = currentGauge.find(".dxg-spindle-hole").clone();
          let border = currentGauge.find(".dxg-spindle-border").clone();
          currentGauge.find(".dxg-title text").first().attr("y", 48);
          currentGauge.find(".dxg-title text").last().attr("y", 28);
          currentGauge.find(".dxg-value-indicator").append(border, circle);
        },
      };
    }

    // Method to initialize the gauge with the configured options
    init() {
      $(this._element).dxCircularGauge(this._buildConfig());
    }
  }

  $(document).ready(function () {
    // Function to update the gauge with the moisture level
    function updateGauge(moistureLevel) {
      $(".gauge").each(function (index, item) {
        // Parameters for initializing GaugeChart
        let params = {
          initialValue: moistureLevel,
          title: `Moisture level`,
          subtitle: `${moistureLevel}`,
        };
        let gauge = new GaugeChart(item, params); // Create GaugeChart instance
        gauge.init(); // Initialize the gauge
      });
    }

    // Function to fetch the moisture level from the server
    function fetchMoistureLevel() {
      $.ajax({
        type: "GET",
        url: "/moisture-level",
        success: function (response) {
          // Update the gauge with the received moisture level
          updateGauge(response.moistureLevel);
        },
        error: function (xhr, status, error) {
          console.error("Error fetching moisture level:", error);
        },
      });
    }

    // Fetch the moisture level from the server when the page loads
    fetchMoistureLevel();

    // Update the moisture level every 15 seconds
    setInterval(fetchMoistureLevel, 15000);
  });
});

/* Function to handle plant selection */
function choosePlant(plantChosen) {
  // Reset all buttons
  document.querySelectorAll('.items button').forEach(button => {
    button.innerText = "Choose";
    button.style.backgroundColor = "#57a0af";
  });

  // Change the text and color of the chosen button
  let chosenButton = document.getElementById(`buttonPlant_${plantChosen}`);
  chosenButton.innerText = "Chosen";
  chosenButton.style.backgroundColor = "#2c525a";
  chosenButton.style.color = "white";

  // Send the chosen plant name to the server
  $.ajax({
    type: 'POST',
    url: '/chosen-plant',
    data: { plant: plantChosen },
    success: function (response) {
      console.log('Chosen plant sent to server successfully.');
    },
    error: function (xhr, status, error) {
      console.error('Error sending chosen plant to server:', error);
    }
  });
}

/* Function to handle image upload */
function uploadImg() {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*';
  fileInput.style.display = 'none';

  fileInput.addEventListener('change', function () {
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    fetch('/upload', {
      method: 'POST',
      body: formData
    })
      .then(response => {
        // Display SweetAlert on success
        Swal.fire({
          icon: 'success',
          title: 'Image Uploaded!',
          text: 'Image sucessfully uploaded',
          timer: 3000,
          showConfirmButton: true
        });
      })
      .catch(error => {
        console.error('Error uploading image:', error);
        const flashMessage = document.getElementById('upload-message');
        flashMessage.textContent = 'An error occurred. Please try again later.';
        flashMessage.classList.remove('hidden');
      });
  });

  document.body.appendChild(fileInput);
  fileInput.click();
  document.body.removeChild(fileInput);
}
