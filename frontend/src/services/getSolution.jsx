import axios from 'axios';

const API_URL = 'http://localhost:5000/solve';

const solveLinearProgramming = async (data) => {
    try {
        const response = await axios.post(API_URL, data, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error solving linear programming:', error);
        throw error;
    }
};

export default solveLinearProgramming;