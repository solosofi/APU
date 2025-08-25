#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <thread>
#include <chrono>
#include <numeric>

struct CpuStats {
    long long user = 0;
    long long nice = 0;
    long long system = 0;
    long long idle = 0;
    long long iowait = 0;
    long long irq = 0;
    long long softirq = 0;
    long long steal = 0;

    long long get_idle_time() const {
        return idle + iowait;
    }

    long long get_total_time() const {
        return user + nice + system + idle + iowait + irq + softirq + steal;
    }
};

std::vector<CpuStats> read_cpu_stats() {
    std::ifstream stat_file("/proc/stat");
    std::string line;
    std::vector<CpuStats> stats;

    while (std::getline(stat_file, line)) {
        if (line.substr(0, 3) == "cpu") {
            std::stringstream ss(line.substr(5));
            CpuStats s;
            ss >> s.user >> s.nice >> s.system >> s.idle >> s.iowait >> s.irq >> s.softirq >> s.steal;
            stats.push_back(s);
        }
    }
    return stats;
}

// This function needs to be thread-safe if called from multiple threads,
// but for our single-threaded Python access, this is fine.
// A more robust implementation would use a class.
static std::vector<CpuStats> prev_stats;
static bool first_call = true;

extern "C" {
    // Returns a JSON string with CPU usage details.
    // This function is stateful. It calculates usage based on the change since its last call.
    const char* get_cpu_usage_json() {
        auto current_stats = read_cpu_stats();

        if (first_call) {
            prev_stats = current_stats;
            first_call = false;
            // Sleep for a short duration to get a valid delta on the first true call
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            current_stats = read_cpu_stats();
        }

        if (prev_stats.empty() || current_stats.empty() || prev_stats.size() != current_stats.size()) {
            prev_stats = current_stats;
            return "{\"error\": \"Reading CPU stats\"}";
        }

        std::stringstream json_ss;
        json_ss << "{";

        // Calculate total CPU usage (first entry)
        long long prev_total_idle = prev_stats[0].get_idle_time();
        long long total_idle = current_stats[0].get_idle_time();
        long long prev_total_time = prev_stats[0].get_total_time();
        long long total_time = current_stats[0].get_total_time();

        double total_delta = total_time - prev_total_time;
        double idle_delta = total_idle - prev_total_idle;
        double total_usage = (total_delta > 0) ? (1.0 - idle_delta / total_delta) * 100.0 : 0.0;

        json_ss << "\"total_usage\": " << total_usage << ",";
        json_ss << "\"per_core_usage\": [";

        // Calculate per-core usage
        for (size_t i = 1; i < current_stats.size(); ++i) {
            long long prev_core_idle = prev_stats[i].get_idle_time();
            long long core_idle = current_stats[i].get_idle_time();
            long long prev_core_total = prev_stats[i].get_total_time();
            long long core_total = current_stats[i].get_total_time();

            double core_total_delta = core_total - prev_core_total;
            double core_idle_delta = core_idle - prev_core_idle;
            double core_usage = (core_total_delta > 0) ? (1.0 - core_idle_delta / core_total_delta) * 100.0 : 0.0;

            json_ss << core_usage << (i == current_stats.size() - 1 ? "" : ",");
        }

        json_ss << "]}";

        prev_stats = current_stats;

        // We need to return a C-string that persists after the function returns.
        // A static string is a simple way to do this for this specific use case.
        // A better solution would involve the caller managing the memory.
        static std::string json_result;
        json_result = json_ss.str();
        return json_result.c_str();
    }

    // High-performance C++ kernel for Sparse Matrix-Vector multiplication (SpMV)
    // using the Compressed Sparse Row (CSR) format.
    void spmv_csr_cpp(
        const double* data,     // Array of non-zero matrix values
        const int* indices,     // Column indices for each non-zero value
        const int* indptr,      // "Index pointer" array
        const double* vector,   // The vector to multiply with
        double* result,         // Output array to store the result
        int num_rows            // Number of rows in the matrix
    ) {
        for (int i = 0; i < num_rows; ++i) {
            double sum = 0.0;
            for (int j = indptr[i]; j < indptr[i+1]; ++j) {
                sum += data[j] * vector[indices[j]];
            }
            result[i] = sum;
        }
    }
}
