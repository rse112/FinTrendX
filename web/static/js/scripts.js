document.addEventListener('DOMContentLoaded', () => {
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    const keywordSelect = document.getElementById('keyword');
    const chartContainer = document.getElementById('chart-container');

    categorySelect.addEventListener('change', updateSubcategoryOptions);
    subcategorySelect.addEventListener('change', updateKeywordOptions);
    keywordSelect.addEventListener('change', updateData);

    function updateSubcategoryOptions() {
        const category = categorySelect.value;

        if (category === 'graph') {
            subcategorySelect.style.display = 'inline-block';
            keywordSelect.style.display = 'none';
            subcategorySelect.innerHTML = `
                <option value="일별급상승">일별 급상승</option>
                <option value="주별급상승">주별 급상승</option>
                <option value="월별급상승">월별 급상승</option>
                <option value="지속상승">지속 상승</option>
                <option value="월별규칙성">월별 규칙성</option>
                <option value="주별지속상승">주별 지속상승</option>
                <option value="월별지속상승">월별 지속상승</option>
                <option value="기타">기타</option>
            `;
        } else {
            subcategorySelect.style.display = 'none';
            keywordSelect.style.display = 'none';
        }
        updateKeywordOptions();
    }

    function updateKeywordOptions() {
        const category = categorySelect.value;
        const subcategory = subcategorySelect.value;

        fetch(`/get_data?category=${category}&subcategory=${subcategory}`)
            .then(response => response.json())
            .then(data => {
                const keywords = data.keywords;
                if (keywords.length > 0) {
                    keywordSelect.style.display = 'inline-block';
                    keywordSelect.innerHTML = keywords.map(kw => `<option value="${kw}">${kw}</option>`).join('');
                } else {
                    keywordSelect.style.display = 'none';
                }
                updateData();
            })
            .catch(error => console.error('Error fetching keywords:', error));
    }

    function updateData() {
        const category = categorySelect.value;
        const subcategory = subcategorySelect.value;
        const keyword = keywordSelect.value;

        fetch(`/get_data?category=${category}&subcategory=${subcategory}&keyword=${keyword}`)
            .then(response => response.json())
            .then(data => {
                updateChart(data.data);
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    function updateChart(data) {
        const ctx = document.getElementById('chart').getContext('2d');
        if (window.myChart) {
            window.myChart.destroy();
        }

        // 데이터가 너무 많으면 최신 100개만 사용
        const limitedData = data.slice(-100);

        const labels = limitedData.map(item => item.Date);
        const values = limitedData.map(item => parseFloat(item.Value));

        window.myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '값',
                    data: values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 페이지가 로드되면 초기 데이터 로드
    updateSubcategoryOptions();
});
