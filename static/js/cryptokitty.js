document.addEventListener("DOMContentLoaded", () => {
    console.log("📈 CryptoKitty Loaded");

    const coinButtons = document.querySelectorAll("#coin-list button");
    const updateButton = document.getElementById("update-prices-btn");
    const selectedCoinsElement = document.getElementById("selected-coins");
    const ctx = document.getElementById("crypto-graph").getContext("2d");
    const flashingBanner = document.getElementById("flashing-banner");
    const topRisersList = document.getElementById("top-risers-list");
    const topNewCoinsList = document.getElementById("top-new-coins-list");

    // Sound Effects
    const sounds = {
        happy: new Audio('/static/sounds/happy.mp3'),
        sniff: new Audio('/static/sounds/sniff.mp3'),
        growl: new Audio('/static/sounds/growl.mp3'),
        bark: new Audio('/static/sounds/bark.mp3')
    };

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

    // Flashing Banner Messages
    let bannerMessages = ["Loading Crypto News..."];
    let currentBannerIndex = 0;

    function updateBanner() {
        flashingBanner.textContent = bannerMessages[currentBannerIndex];
        currentBannerIndex = (currentBannerIndex + 1) % bannerMessages.length;
    }

    setInterval(updateBanner, 3000);

    // CryptoDog Sound Logic
    let soundEnabled = true;

    function playSound(type) {
        if (soundEnabled && sounds[type]) {
            sounds[type].play();
        }
    }

    document.getElementById("crypto-dog-toggle").addEventListener("change", (e) => {
        soundEnabled = e.target.checked;
    });

    // Update Top Movers
    function updateTopMovers() {
        fetch('/top_risers')
            .then(response => response.json())
            .then(data => {
                topRisersList.innerHTML = '';
                data.top_risers.forEach(coin => {
                    const li = document.createElement('li');
                    li.textContent = coin;
                    topRisersList.appendChild(li);
                });
                bannerMessages.push(`🚀 Top Risers: ${data.top_risers.join(', ')}`);
            });

        fetch('/top_new_coins')
            .then(response => response.json())
            .then(data => {
                topNewCoinsList.innerHTML = '';
                data.top_new_coins.forEach(coin => {
                    const li = document.createElement('li');
                    li.textContent = coin;
                    topNewCoinsList.appendChild(li);
                });
                bannerMessages.push(`🌟 New Coins: ${data.top_new_coins.join(', ')}`);
            });
    }

    setInterval(updateTopMovers, 30000);

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

        fetch('/prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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

            let positiveCount = 0;
            let negativeCount = 0;

            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                const coinElement = document.createElement('li');
                coinElement.textContent = `${coin}: $${coinData.price} (${coinData.change}%)`;
                coinElement.style.color = coinData.change < 0 ? 'red' : 'green';
                selectedCoinsElement.appendChild(coinElement);

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

                if (coinData.change > 0) positiveCount++;
                if (coinData.change < 0) negativeCount++;
            });

            if (positiveCount > negativeCount) {
                playSound('happy');
                bannerMessages.push("🚀 Market is on the rise!");
            } else if (negativeCount > positiveCount) {
                playSound('growl');
                bannerMessages.push("📉 Market is dropping!");
            } else {
                playSound('sniff');
                bannerMessages.push("💤 Market is stable.");
            }

            cryptoChart.update();
        })
        .catch(error => console.error('Error fetching prices:', error));
    });
});
