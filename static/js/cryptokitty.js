// Update Prices Button Logic (Preserved and Fixed)
updateButton.addEventListener("click", () => {
    const selectedCoins = Array.from(coinButtons)
        .filter(button => button.classList.contains("active"))
        .map(button => button.value);

    if (selectedCoins.length === 0) {
        alert("Please select at least one coin.");
        return;
    }

    console.log("🚀 Sending price request for:", selectedCoins);

    fetch("/prices", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ coins: selectedCoins })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
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
    .catch(error => console.error("Error fetching prices:", error));
});
