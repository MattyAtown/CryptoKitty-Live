// CryptoKitty Main Logic

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

    const sounds = {
        happy: new Audio('/static/sounds/happy.mp3'),
        sniff: new Audio('/static/sounds/sniff.mp3'),
        growl: new Audio('/static/sounds/growl.mp3'),
        bark: new Audio('/static/sounds/bark.mp3')
    };

    const dogImages = {
        happy: '/static/images/happy.png',
        neutral: '/static/images/neutral.png',
        angry: '/static/images/angry.png',
        excited: '/static/images/excited.png'
    };

    let cryptoDogActive = false;
    const dogImage = document.getElementById("crypto-dog-img");
    const banner = document.getElementById("flashing-banner");
    const risersList = document.getElementById("top-risers-list");
    const newCoinsList = document.getElementById("top-new-coins-list");

    function updateDogState(state) {
        if (cryptoDogActive) {
            dogImage.src = dogImages[state];
            sounds[state].play();
        }
    }

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

            let positiveCount = 0;
            let negativeCount = 0;

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                const coinElement = document.createElement('li');
                const status = coinData.change > 0 ? "Rising" : coinData.change < 0 ? "Falling" : "Stable";
                coinElement.textContent = `${coin}: $${coinData.price} (${coinData.change}%) - ${status}`;
                coinElement.style.color = coinData.change < 0 ? 'red' : 'green';
                coinListElement.appendChild(coinElement);

                if (coinData.change > 0) positiveCount++;
                if (coinData.change < 0) negativeCount++;

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

            // Update CryptoDog State
            if (positiveCount > negativeCount) {
                updateDogState('happy');
                banner.textContent = "Market is Warming Up! 🚀";
            } else if (negativeCount > positiveCount) {
                updateDogState('angry');
                banner.textContent = "Market is Falling! 📉";
            } else {
                updateDogState('neutral');
                banner.textContent = "Stable Market... 💤";
            }

            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    }

    function updateTopMovers() {
        fetch('/top_risers')
        .then(response => response.json())
        .then(data => {
            const topRisers = data.top_risers;
            risersList.innerHTML = '';
            topRisers.forEach(coin => {
                const li = document.createElement('li');
                li.textContent = coin;
                risersList.appendChild(li);
            });
        });

        fetch('/top_new_coins')
        .then(response => response.json())
        .then(data => {
            const topNewCoins = data.top_new_coins;
            newCoinsList.innerHTML = '';
            topNewCoins.forEach(coin => {
                const li = document.createElement('li');
                li.textContent = coin;
                newCoinsList.appendChild(li);
            });
        });
    }

    document.getElementById('update-prices-btn').addEventListener('click', updateSelectedCoins);

    document.getElementById('select-all').addEventListener('click', () => {
        document.querySelectorAll('#coin-list input[type="checkbox"]').forEach(checkbox => checkbox.checked = true);
        updateSelectedCoins();
    });

    document.getElementById('deselect-all').addEventListener('click', () => {
        document.querySelectorAll('#coin-list input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);
        updateSelectedCoins();
    });

    document.getElementById("crypto-dog-toggle").addEventListener("change", (e) => {
        cryptoDogActive = e.target.checked;
        updateDogState("neutral");
    });

    // Initial Data Fetch
    updateTopMovers();
    setInterval(updateTopMovers, 30000);  // Update every 30 seconds
});
