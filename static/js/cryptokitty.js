document.addEventListener("DOMContentLoaded", () => {
    console.log("📈 CryptoKitty Loaded");

    const coinButtons = document.querySelectorAll("#coin-list button");
    const updateButton = document.getElementById("update-prices-btn");
    const selectedCoinsElement = document.getElementById("selected-coins");
    const ctx = document.getElementById("crypto-graph").getContext("2d");

    // Initialize the chart
    const cryptoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Time' } },
                y: { title: { display: true, text: 'Percentage Change (%)' }, min: -100, max: 100 }
            }
        }
    });

    // Button Click Logic
    coinButtons.forEach(button => {
        button.addEventListener("click", () => {
            button.classList.toggle("active");
        });
    });

    // Update Prices Button Logic
    updateButton.addEventListener("click", () => {
        const selectedCoins = Array.from(coinButtons)
            .filter(button => button.classList.contains("active"))
            .map(button => button.value);

        if (selectedCoins.length === 0) {
            alert("Please select at least one coin.");
            return;
        }

        console.log("🚀 Sending price request for:", selectedCoins);

        fetch("https://cryptokitty-live.onrender.com/prices", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ coins: selectedCoins })
        })
        .then(response => response.json())
        .then(data => {
            console.log("💰 Prices Data:", data);
            selectedCoinsElement.innerHTML = '';
            const now = new Date().toLocaleTimeString();

            if (!cryptoChart.data.labels.includes(now)) {
                cryptoChart.data.labels.push(now);
                if (cryptoChart.data.labels.length > 12) cryptoChart.data.labels.shift();
            }

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                // Add to Selected Coins List
                const coinElement = document.createElement('li');
                coinElement.textContent = `${coin}: $${coinData.price} (${coinData.change}%)`;
                coinElement.style.color = coinData.change < 0 ? 'red' : 'green';
                selectedCoinsElement.appendChild(coinElement);

                // Update Chart
                let dataset = cryptoChart.data.datasets.find(ds => ds.label === coin);
                if (!dataset) {
                    dataset = {
                        label: coin,
                        data: [],
                        borderColor: '#' + Math.floor(Math.random() * 16777215).toString(16),
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    };
                    cryptoChart.data.datasets.push(dataset);
                }

                dataset.data.push(coinData.change);
                if (dataset.data.length > 12) dataset.data.shift();
            });

            cryptoChart.update();
        })
        .catch(error => {
            console.error("Error fetching prices:", error);
            alert("⚠️ Error fetching prices. Please try again later.");
        });
    });
});
