<!DOCTYPE html>
<html>
<head>
	<title>Sortable Table</title>
	<style>
		table {
			border-collapse: collapse;
			width: 100%;
		}
		th, td {
			text-align: left;
			padding: 8px;
			border: 1px solid #ddd;
		}
		tr:nth-child(even) {
			background-color: #f2f2f2;
		}
		th {
			background-color: #4CAF50;
			color: white;
			cursor: pointer;
		}
	</style>
	<script>
		function sortTable(n) {
		  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
		  table = document.getElementById("myTable");
		  switching = true;
		  dir = "asc";
		  while (switching) {
		    switching = false;
		    rows = table.rows;
		    for (i = 1; i < (rows.length - 1); i++) {
		      shouldSwitch = false;
		      x = rows[i].getElementsByTagName("TD")[n];
		      y = rows[i + 1].getElementsByTagName("TD")[n];
		      if (dir == "asc") {
		        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
		          shouldSwitch= true;
		          break;
		        }
		      } else if (dir == "desc") {
		        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
		          shouldSwitch = true;
		          break;
		        }
		      }
		    }
		    if (shouldSwitch) {
		      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
		      switching = true;
		      switchcount ++;
		    } else {
		      if (switchcount == 0 && dir == "asc") {
		        dir = "desc";
		        switching = true;
		      }
		    }
		  }
		}
	</script>
</head>
<body>
	<table id="myTable">
		<thead>
			<tr>
				<th onclick="sortTable(0)">Name</th>
				<th onclick="sortTable(1)">Age</th>
				<th onclick="sortTable(2)">Gender</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>John</td>
				<td>32</td>
				<td>Male</td>
			</tr>
			<tr>
				<td>Jane</td>
				<td>27</td>
				<td>Female</td>
			</tr>
			<tr>
				<td>Michael</td>
				<td>45</td>
				<td>Male</td>
			</tr>
			<tr>
				<td>Samantha</td>
				<td>29</td>
				<td>Female</td>
			</tr>
			<tr>
				<td>David</td>
				<td>38</td>
				<td>Male</td>
			</tr>
			<tr>
				<td>Emily</td>
				<td>31</td>
				<td>Female</td>
			</tr>
			<tr>
				<td>Christopher</td>
				<td>41</td>
				<td>Male</td>
			</tr>
			<tr>
				<td>Olivia</td>
				<td>26</td>
				<td>Female</td>
			</tr>
			<tr>
				<td>Robert</td>
				<td
				41</td>
				<td>Male</td>
				</tr>
				<tr>
				<td>Isabella</td>
				<td>24</td>
				<td>Female</td>
				</tr>
				</tbody>
			</table>	
		</body>
</html>
