document.addEventListener("DOMContentLoaded", () => {
    console.log("📈 CryptoKitty Loaded");

    const cryptoChart = new Chart(document.getElementById('crypto-graph').getContext('2d'), {
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

    function updateSelectedCoins() {
        const selectedCoins = [];
        const coinListElement = document.getElementById('selected-coins');
        coinListElement.innerHTML = '';

        document.querySelectorAll('#coin-list input[type="checkbox"]:checked').forEach(checkbox => {
            selectedCoins.push(checkbox.value);
        });

        if (selectedCoins.length === 0) return;

        fetch('/prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coins: selectedCoins })
        })
        .then(response => response.json())
        .then(data => {
            console.log("💰 Prices Data:", data);
            const now = new Date().toLocaleTimeString();
            const labels = cryptoChart.data.labels;

            if (labels.length === 0 || labels[labels.length - 1] !== now) {
                labels.push(now);
                if (labels.length > 12) labels.shift();
            }

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                // Add to list
                const coinElement = document.createElement('li');
                coinElement.textContent = `${coin}: $${coinData.price} (${coinData.change}%)`;
                coinElement.style.color = coinData.change < 0 ? 'red' : 'green';
                coinListElement.appendChild(coinElement);

                // Update graph
                if (!cryptoChart.data.datasets.some(ds => ds.label === coin)) {
                    cryptoChart.data.datasets.push({
                        label: coin,
                        data: [],
                        borderColor: '#' + Math.floor(Math.random()*16777215).toString(16),
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    });
                }

                const dataset = cryptoChart.data.datasets.find(ds => ds.label === coin);
                dataset.data.push(coinData.change);
                if (dataset.data.length > 12) dataset.data.shift();
            });

            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    }

    document.getElementById('update-prices-btn').addEventListener('click', updateSelectedCoins);
});
