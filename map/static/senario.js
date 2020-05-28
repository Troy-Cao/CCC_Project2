$(
	function(){
		var myChart = echarts.init(document.getElementById('map'));
		$.get('../static/Melbourne.json',function(geoJson){
			echarts.registerMap('Melbourne',geoJson,{});
			var option = {
				tooltip: {
					trigger: 'item',
					// formatter: '{b}<br/>{c} (p / km2)'
				},
				visualMap: {
					min: 500,
					max: 50000,
					text:['High','Low'],
					left: 'right',
					realtime: false,
					calculable: true,
					inRange: {
						color: ['#313695','#4575b4', '#74add1','#abd9e9','#e0f3f8']
					}
				},
				series: [
					{
						name: '',
						type: 'map',
						mapType: 'Melbourne',
						aspectScale: 0.85,  //地图长度比
						label: {
							normal: {
								show: true,
								textStyle: {
									color: '#fff'
								}
							},
							emphasis: {
								show: true,
								textStyle: {
									color: '#333'
								}
							}
						},
						data: [
							{name: 'Docklands', value: 17000},
							{name: 'Melbourne', value: 1000},
							{name: ' ', value: 20000},
							{name: 'Southbank', value: 20000},
							{name: 'Port Melbourne', value: 25000},
							{name: 'West Melbourne', value: 30000},
							{name: 'North Melbourne', value: 18000},
							{name: 'Parkville', value: 2300},
							{name: 'Carlton', value: 20000},
							{name: 'Carlton North', value: 16000},
							{name: 'East Melbourne', value: 28000},
							{name: 'South Yarra', value: 18000},
							{name: 'Kenslngton', value: 8000},
							{name: 'Flemlngton', value: 3000},
						]
					}                              
				]
			};
			myChart.setOption(option);
		});
	}
);