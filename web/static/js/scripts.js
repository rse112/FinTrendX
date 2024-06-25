document.addEventListener('DOMContentLoaded', () => {
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    const keywordSelect = document.getElementById('keyword');
    const chartContainer = document.getElementById('chart-container');
    const dataTable = document.getElementById('data-table').getElementsByTagName('tbody')[0];

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

                <option value="월별규칙성">월별 규칙성</option>
                <option value="주별지속상승">주별 지속상승</option>
                <option value="월별지속상승">월별 지속상승</option>

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
                updateChart(data.graph_data);
                updateTable(data.info_data);
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

    function updateTable(data) {
        dataTable.innerHTML = ''; // 기존 데이터를 제거합니다.

        data.forEach(item => {
            let row = dataTable.insertRow();
            let cellDate = row.insertCell(0);
            let cellValue = row.insertCell(1);
            let cellExtra1 = row.insertCell(2);
            let cellExtra2 = row.insertCell(3);
            let cellExtra3 = row.insertCell(4);
            let cellExtra4 = row.insertCell(5);
            let cellExtra5 = row.insertCell(6);
            let cellExtra6 = row.insertCell(7);
            let cellExtra7 = row.insertCell(8);

            cellDate.textContent = item.Date;
            cellValue.textContent = item.Value;
            cellExtra1.textContent = item.Extra1;
            cellExtra2.textContent = item.Extra2;
            cellExtra3.textContent = item.Extra3;
            cellExtra4.textContent = item.Extra4;
            cellExtra5.textContent = item.Extra5;
            cellExtra6.textContent = item.Extra6;
            cellExtra7.textContent = item.Extra7;
        });
    }

    // 페이지가 로드되면 초기 데이터 로드
    updateSubcategoryOptions();
});
