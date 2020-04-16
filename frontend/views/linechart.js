var parseTime = d3.timeParse("%Y");
var formatTime = d3.timeFormat("%Y");

d3.csv("neurips_pubnum_by_year.csv", function (d) {
    return {
        count: d.id,
        year: parseTime(d.year)
    };

}).then(function (data) {
    plot1(data);
});

function plot1(data) {
    var margin = {top: 100, right: 250, bottom: 150, left: 250}
    , width = window.innerWidth - margin.left - margin.right // Use the window's width 
    , height = window.innerHeight - margin.top - margin.bottom; // Use the window's height

    var startDate = d3.min(data, function(d) { return d.year; });
    var endDate = d3.max(data, function(d) { return d.year; });

    var xScale = d3.scaleTime()
      .domain([
        d3.timeDay.offset(startDate,-1),
        d3.timeDay.offset(endDate,1)
      ]) // input
      .range([0, width]); // output

    var yScale = d3.scaleLinear()
      .domain([0, d3.max(data, function(d){ return d.count })]) // input 
      .range([height, 0]); // output 

    var line = d3.line()
      .x(function (d) {return xScale(d.year);})
      .y(function (d) {return yScale(d.count);})
      .curve(d3.curveMonotoneX)
    
    var svg = d3.select("#plot1").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

    svg.append("g")
      .attr("class", "y axis")
      .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

    svg.append("path")
      .datum(data)
      .attr("class","line")
      .attr("d",line)
      .attr("fill", "none")
      .attr("stroke", "#FFC300")
      .attr("stroke-width",1);
}