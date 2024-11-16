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

const LineGraph = () => {
    // Initial data
    const initialData = {
        labels: ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
        datasets: [
            {
                label: "Dynamic Line Data",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 2,
                pointRadius: 3,
                data: [12, 19, 3, 5, 2],
            },
        ],
    };

    const [chartData, setChartData] = useState(initialData);

    // Function to update data
    const updateData = () => {
        const newDataPoint = Math.floor(Math.random() * 20) + 1; // Generate random data
        setChartData((prev) => {
            const updatedData = [...prev.datasets[0].data.slice(1), newDataPoint]; // Shift left and add new data
            return {
                ...prev,
                datasets: [
                    {
                        ...prev.datasets[0],
                        data: updatedData,
                    },
                ],
            };
        });
    };

    // Chart options
    const options = {
        responsive: true,
        maintainAspectRatio: false, // Enable custom sizing
        animation: {
            duration: 1000, // Animation duration
            easing: "easeOutCubic", // Animation easing
        },
        plugins: {
            legend: {
                display: true,
                position: "top",
            },
            title: {
                display: true,
                text: "Dynamic Line Graph",
            },
        },
        scales: {
            x: {
                beginAtZero: true,
            },
            y: {
                beginAtZero: true,
            },
        },
    };

    // Periodically update data
    useEffect(() => {
        const interval = setInterval(updateData, 2000); // Update every 2 seconds
        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    return (
        <div className="w-full max-w-md mx-auto bg-white p-4 shadow-md rounded-md">
            <div className="relative h-64">
                <Line data={chartData} options={options} />
            </div>
        </div>
    );
};

export default LineGraph;