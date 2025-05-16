// CryptoKitty Main Logic

document.addEventListener("DOMContentLoaded", () => {
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

    const coinDatasets = {};
    let cryptoDogActive = false;

    function updateSelectedCoins() {
        const selectedCoins = [];
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
            const now = new Date().toLocaleTimeString();
            const labels = cryptoChart.data.labels;

            if (labels.length === 0 || labels[labels.length - 1] !== now) {
                labels.push(now);
                if (labels.length > 12) labels.shift();
            }

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                const latestPrice = coinData.price;
                const latestChange = coinData.change;
                const percentageChanges = coinData.percentage_changes;

                // Create or update dataset
                if (!coinDatasets[coin]) {
                    coinDatasets[coin] = {
                        label: coin,
                        data: [],
                        borderColor: '#' + Math.floor(Math.random()*16777215).toString(16),
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    };
                    cryptoChart.data.datasets.push(coinDatasets[coin]);
                }

                // Update dataset
                coinDatasets[coin].data.push(latestChange);
                if (coinDatasets[coin].data.length > 12) coinDatasets[coin].data.shift();

                // Update coin list
                const coinElement = document.getElementById(`coin-${coin}`);
                coinElement.textContent = `${coin}: $${latestPrice} (${latestChange}%)`;
                coinElement.style.color = latestChange < 0 ? 'red' : 'green';

                // Handle CryptoDog
                if (coin === 'BTC' && cryptoDogActive) {
                    updateCryptoDog(percentageChanges);
                }
            });

            // Update graph
            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    }

    // Set up event listeners
    document.getElementById('update-prices-btn').addEventListener('click', updateSelectedCoins);
    document.getElementById('crypto-dog-toggle').addEventListener('change', (event) => {
        cryptoDogActive = event.target.checked;
    });
});
