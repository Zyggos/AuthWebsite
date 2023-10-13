const api = "http://127.0.0.1:5000";

window.onload = () => {
  const searchButton = document.querySelector(".search-btn");
  searchButton.addEventListener("click", searchButtonOnClick);
};

searchButtonOnClick = () => {
  const searchInput = document.querySelector("#search");
  const searchTerm = searchInput.value;

  fetch(`${api}/search?name=${searchTerm}`)
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        console.log(`HTTP status ${response.status}: ${response.statusText}`);
      }
    })
    .then((results) => {
      if (results) {
        const resultsTable = document.querySelector("#results");

        resultsTable.innerHTML = `
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Production year</th>
            <th>Price</th>
            <th>Color</th>
            <th>Size</th>
          </tr>
        `;

        results.forEach((result) => {
          const row = resultsTable.insertRow();
          row.innerHTML = `
            <td>${result.id}</td>
            <td>${result.name}</td>
            <td>${result.production_year}</td>
            <td>${result.price}</td>
            <td>${result.color}</td>
            <td>${result.size}</td>
          `;
        });
      }
    })
    .catch((error) => console.error(error));
};

productFormOnSubmit = (event) => {
  event.preventDefault();
  const name = document.querySelector("#name").value;
  const productionYear = document.querySelector("#prod_year").value;
  const price = document.querySelector("#price").value;
  const color = document.querySelector("#color").value;
  const size = document.querySelector("#size").value;

  const formData = {
    name: name,
    production_year: parseInt(productionYear),
    price: parseFloat(price),
    color: parseInt(color),
    size: parseInt(size)
  };

  fetch(`${api}/add-product`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(formData)
  })
    .then((response) => {
      if (response.status === 200) {
        alert("OK");

        document.querySelector("#name").value = "";
        document.querySelector("#prod_year").value = "";
        document.querySelector("#price").value = "";
        document.querySelector("#color").value = "";
        document.querySelector("#size").value = "";
      } else {
        console.log(`HTTP status ${response.status}: ${response.statusText}`);
      }
    })
    .catch((error) => console.error(error));
};

