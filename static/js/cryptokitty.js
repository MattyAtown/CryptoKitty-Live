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
                y: { title: { display: true, text: 'Price (USD)' } }
            }
        }
    });

    const coinDatasets = {};
    let cryptoDogActive = false;
    const sounds = {
        excited: new Audio('/static/sounds/bark.mp3'),
        happy: new Audio('/static/sounds/happy.mp3'),
        angry: new Audio('/static/sounds/growl.mp3'),
        neutral: new Audio('/static/sounds/sniff.mp3')
    };

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
            const now = new Date().toLocaleTimeString();
            const labels = cryptoChart.data.labels;

            if (labels.length === 0 || labels[labels.length - 1] !== now) {
                labels.push(now);
                if (labels.length > 20) labels.shift();
            }

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                const latestPrice = coinData.prices.slice(-1)[0];
                const change = coinData.change;

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
                coinDatasets[coin].data.push(latestPrice);
                if (coinDatasets[coin].data.length > 20) coinDatasets[coin].data.shift();

                // Update coin list
                const priceElement = document.createElement('li');
                priceElement.textContent = `${coin}: $${latestPrice} (${change}%)`;
                coinListElement.appendChild(priceElement);

                // Handle CryptoDog logic for BTC
                if (coin === 'BTC' && cryptoDogActive) {
                    updateCryptoDog(coinData.percentage_changes);
                }
            });

            // Update graph
            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    }

    function updateCryptoDog(percentageChanges) {
        const dogImg = document.getElementById('crypto-dog-img');
        const changeSum = percentageChanges.slice(-5).reduce((acc, val) => acc + val, 0);

        if (percentageChanges.slice(-3).every(p => p > 0)) {
            dogImg.src = '/static/images/excited.png';
            playSound('excited');
            updateBanner("Market is getting busy");
        } else if (changeSum > 0) {
            dogImg.src = '/static/images/happy.png';
            playSound('happy');
            updateBanner("Good Market");
        } else if (changeSum < 0) {
            dogImg.src = '/static/images/angry.png';
            playSound('angry');
            updateBanner("Market Downturn");
        } else {
            dogImg.src = '/static/images/neutral.png';
            playSound('neutral');
            updateBanner("Market Stable");
        }
    }

    function playSound(type) {
        if (sounds[type]) {
            sounds[type].play();
        }
    }

    function updateBanner(message) {
        const banner = document.getElementById('flashing-banner');
        banner.textContent = message;
        setTimeout(fetchTopRisers, 15000);  // Switch back to top risers every 15 seconds
    }

    function fetchTopRisers() {
        fetch('/top_risers')
            .then(response => response.json())
            .then(data => {
                const banner = document.getElementById('flashing-banner');
                banner.textContent = data.top_risers.join(' | ');
            })
            .catch(error => console.error('Error fetching top risers:', error));
    }

    document.getElementById('crypto-dog-toggle').addEventListener('change', (event) => {
        cryptoDogActive = event.target.value === 'on';
    });

    // Initial load
    fetchTopRisers();
    setInterval(updateSelectedCoins, 60000);  // Update every 60 seconds
});
