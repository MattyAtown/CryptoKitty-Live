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
                y: { title: { display: true, text: 'Percentage Change' } }
            }
        }
    });

    function updateSelectedCoins() {
        const selectedCoins = [];
        document.querySelectorAll('#coin-list input[type="checkbox"]:checked').forEach(checkbox => {
            selectedCoins.push(checkbox.value);
        });

        fetch('/prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coins: selectedCoins })
        })
        .then(response => response.json())
        .then(data => {
            const now = new Date().toLocaleTimeString();
            const datasets = [];
            document.getElementById('selected-coins').innerHTML = '';

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                datasets.push({
                    label: coin,
                    data: coinData.prices,
                    borderColor: '#' + Math.floor(Math.random()*16777215).toString(16),
                    borderWidth: 2,
                    fill: false
                });

                const priceElement = document.createElement('li');
                const latestPrice = coinData.prices.slice(-1)[0];
                const change = coinData.change;
                priceElement.textContent = `${coin}: $${latestPrice} (${change}%)`;
                document.getElementById('selected-coins').appendChild(priceElement);
            });

            cryptoChart.data.labels.push(now);
            cryptoChart.data.datasets = datasets;
            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    }

    function toggleCryptoDog() {
        const dogToggle = document.getElementById('crypto-dog-toggle').value;
        const dogImg = document.getElementById('crypto-dog-img');

        if (dogToggle === 'on') {
            fetch('/prices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ coins: ['BTC'] })
            })
            .then(response => response.json())
            .then(data => {
                const btc = data.prices.BTC;
                const lastPrice = btc.prices.slice(-1)[0];
                const firstPrice = btc.prices[0];
                const percentageChange = ((lastPrice - firstPrice) / firstPrice) * 100;

                if (percentageChange > 2) {
                    dogImg.src = '/static/images/excited.png';
                } else if (percentageChange < -2) {
                    dogImg.src = '/static/images/angry.png';
                } else if (percentageChange > 0) {
                    dogImg.src = '/static/images/happy.png';
                } else {
                    dogImg.src = '/static/images/neutral.png';
                }
            })
            .catch(error => console.error('Error fetching BTC price:', error));
        } else {
            dogImg.src = '/static/images/neutral.png';
        }
    }

    // Initial load
    updateSelectedCoins();
    setInterval(updateSelectedCoins, 60000);  // Update every 60 seconds
});
