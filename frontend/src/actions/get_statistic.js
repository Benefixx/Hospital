import axios from "axios";

async function getStatistic(uid, token) {
    try {
        let response = await axios.get("http://127.0.0.1:8000/auth/statistic")
        return response.data
    } catch {
        return false
    }
}
  
export default getStatistic;