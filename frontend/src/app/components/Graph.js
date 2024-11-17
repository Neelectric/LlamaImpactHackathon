import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const LineGraph = ({ judgements }) => {
    // Fallback for when no judgements are available
    if (!judgements || judgements.length === 0) {
        return (
            <div className="text-center p-4 bg-gray-100 rounded-md shadow-md">
                <p className="text-gray-500">No data available to display.</p>
            </div>
        );
    }

    // Initial chart data
    const initialData = {
        labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        datasets: [
            {
                label: `Natural Disaster Score`,
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 2,
                pointRadius: 5,
                pointBackgroundColor: "rgba(255, 99, 132, 1)",
                pointHoverRadius: 7,
                data: [0, 0, 0, 0, 0],
            },
        ],
    };

    const [chartData, setChartData] = useState(initialData);

    // Function to compute running average
    const computeRunningAverage = (data, numPoints) => {
        const averages = [];
        for (let i = 0; i < numPoints; i++) {
            if (i < data.length) {
                const slice = data.slice(0, i + 1); // Take judgements up to the current index
                const average = slice.reduce((sum, item) => sum + item.judgeval, 0) / slice.length;
                averages.push(average);
            } else {
                averages.push(0); // Default to 0 if there are not enough points
            }
        }
        return averages.reverse();
    };

    // Update chart data whenever judgements change
    useEffect(() => {
        const numPoints = 5; // Number of points on the graph
        const averages = computeRunningAverage(judgements, numPoints);

        setChartData((prevData) => ({
            ...prevData,
            datasets: [
                {
                    ...prevData.datasets[0],
                    data: averages, // Update with running average data
                },
            ],
        }));
    }, [judgements]);

    // Chart options
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: "top",
                labels: {
                    font: {
                        size: 14,
                        family: "'Inter', sans-serif",
                        weight: "500",
                    },
                    color: "white",
                },
            },
            title: {
                display: true,
                text: judgements.length > 0 
                    ? `Local Natural Disaster Score for ${judgements[0].location_name}`
                    : "Local Natural Disaster Score",
                font: {
                    size: 18,
                    family: "'Inter', sans-serif",
                    weight: "600",
                },
                color: "#ffffff",
            },
        },
        scales: {
            x: {
                grid: {
                    color: "rgba(200, 200, 200, 0.2)",
                },
                ticks: {
                    font: {
                        size: 12,
                        family: "'Inter', sans-serif",
                    },
                    color: "#ffffff",
                },
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: "rgba(200, 200, 200, 0.2)",
                },
                ticks: {
                    font: {
                        size: 12,
                        family: "'Inter', sans-serif",
                    },
                    color: "#ffffff",
                },
            },
        },
    };

    return (
        <div className="w-full max-w-lg mx-auto bg-white p-6 shadow-lg rounded-md">
            <div className="relative" style={{ height: "300px" }}>
                <Line data={chartData} options={options} />
            </div>
        </div>
    );
};

export default LineGraph;