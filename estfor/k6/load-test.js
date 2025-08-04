/**
 * K6 Load Test for EstFor Asset Collection System
 *
 * This script performs comprehensive load testing including:
 * - Smoke tests
 * - Load tests
 * - Stress tests
 * - Spike tests
 * - Breakpoint tests
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const assetCreationTime = new Trend("asset_creation_time");
const assetRetrievalTime = new Trend("asset_retrieval_time");
const healthCheckTime = new Trend("health_check_time");
const assetCount = new Counter("assets_created");

// Test configuration
export const options = {
  // Smoke test - verify system works
  smoke: {
    vus: 1,
    duration: "30s",
    thresholds: {
      http_req_duration: ["p(95)<500"],
      errors: ["rate<0.1"],
    },
  },

  // Load test - normal load
  load: {
    vus: 10,
    duration: "2m",
    thresholds: {
      http_req_duration: ["p(95)<1000"],
      errors: ["rate<0.05"],
    },
  },

  // Stress test - beyond normal capacity
  stress: {
    vus: 50,
    duration: "5m",
    thresholds: {
      http_req_duration: ["p(95)<2000"],
      errors: ["rate<0.1"],
    },
  },

  // Spike test - sudden load increase
  spike: {
    stages: [
      { duration: "30s", target: 10 }, // Ramp up
      { duration: "1m", target: 100 }, // Spike
      { duration: "30s", target: 10 }, // Ramp down
    ],
    thresholds: {
      http_req_duration: ["p(95)<3000"],
      errors: ["rate<0.15"],
    },
  },

  // Breakpoint test - find system limits
  breakpoint: {
    vus: 1,
    duration: "10m",
    thresholds: {
      http_req_duration: ["p(95)<5000"],
      errors: ["rate<0.2"],
    },
  },
};

// Test data
const testAssets = [
  {
    name: "Load Test Sword",
    type: "weapon",
    rarity: "common",
    description: "Sword created during load testing",
  },
  {
    name: "Load Test Shield",
    type: "armor",
    rarity: "rare",
    description: "Shield created during load testing",
  },
  {
    name: "Load Test Potion",
    type: "consumable",
    rarity: "epic",
    description: "Potion created during load testing",
  },
];

// Helper function to get random asset data
function getRandomAsset() {
  const asset = testAssets[Math.floor(Math.random() * testAssets.length)];
  return {
    ...asset,
    name: `${asset.name}_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`,
  };
}

// Main test function
export default function () {
  const baseUrl = __ENV.BASE_URL || "http://localhost:8000";

  // Test 1: Health Check
  const healthCheck = () => {
    const startTime = Date.now();
    const response = http.get(`${baseUrl}/health`);
    const duration = Date.now() - startTime;

    healthCheckTime.add(duration);

    const healthCheckResult = check(response, {
      "health check status is 200": (r) => r.status === 200,
      "health check response time < 500ms": (r) => r.timings.duration < 500,
      "health check has correct content type": (r) =>
        r.headers["Content-Type"].includes("application/json"),
    });

    errorRate.add(!healthCheckResult);

    if (!healthCheckResult) {
      console.error(
        `Health check failed: ${response.status} - ${response.body}`
      );
    }
  };

  // Test 2: Asset Creation
  const createAsset = () => {
    const assetData = getRandomAsset();
    const startTime = Date.now();

    const response = http.post(
      `${baseUrl}/assets/`,
      JSON.stringify(assetData),
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const duration = Date.now() - startTime;
    assetCreationTime.add(duration);

    const createResult = check(response, {
      "asset creation status is 200": (r) => r.status === 200,
      "asset creation response time < 1000ms": (r) => r.timings.duration < 1000,
      "asset creation returns valid JSON": (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.id && data.name === assetData.name;
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!createResult);

    if (createResult) {
      assetCount.add(1);
      return JSON.parse(response.body).id;
    }

    return null;
  };

  // Test 3: Asset Retrieval
  const retrieveAsset = (assetId) => {
    if (!assetId) return;

    const startTime = Date.now();
    const response = http.get(`${baseUrl}/assets/${assetId}`);
    const duration = Date.now() - startTime;

    assetRetrievalTime.add(duration);

    const retrieveResult = check(response, {
      "asset retrieval status is 200": (r) => r.status === 200,
      "asset retrieval response time < 500ms": (r) => r.timings.duration < 500,
      "asset retrieval returns valid JSON": (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.id === assetId;
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!retrieveResult);
  };

  // Test 4: Asset Listing
  const listAssets = () => {
    const response = http.get(`${baseUrl}/assets/?limit=10`);

    const listResult = check(response, {
      "asset listing status is 200": (r) => r.status === 200,
      "asset listing response time < 1000ms": (r) => r.timings.duration < 1000,
      "asset listing returns array": (r) => {
        try {
          const data = JSON.parse(r.body);
          return Array.isArray(data);
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!listResult);
  };

  // Test 5: Asset Statistics
  const getAssetStats = () => {
    const response = http.get(`${baseUrl}/assets/stats/summary`);

    const statsResult = check(response, {
      "asset stats status is 200": (r) => r.status === 200,
      "asset stats response time < 500ms": (r) => r.timings.duration < 500,
      "asset stats returns valid data": (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.total_assets !== undefined;
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!statsResult);
  };

  // Test 6: Asset Collection Trigger
  const triggerAssetCollection = () => {
    const response = http.post(`${baseUrl}/assets/collect`);

    const collectionResult = check(response, {
      "asset collection trigger status is 200": (r) => r.status === 200,
      "asset collection trigger response time < 2000ms": (r) =>
        r.timings.duration < 2000,
      "asset collection trigger returns task info": (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.task_id && data.status === "queued";
        } catch (e) {
          return false;
        }
      },
    });

    errorRate.add(!collectionResult);
  };

  // Test 7: Error Handling
  const testErrorHandling = () => {
    // Test invalid asset ID
    const invalidResponse = http.get(`${baseUrl}/assets/invalid_id_12345`);

    const errorResult = check(invalidResponse, {
      "invalid asset returns 404": (r) => r.status === 404,
      "error response time < 500ms": (r) => r.timings.duration < 500,
    });

    errorRate.add(!errorResult);
  };

  // Execute test scenarios
  const scenario = Math.random();

  if (scenario < 0.3) {
    // 30% - Health checks
    healthCheck();
    getAssetStats();
  } else if (scenario < 0.6) {
    // 30% - Asset operations
    const assetId = createAsset();
    retrieveAsset(assetId);
    listAssets();
  } else if (scenario < 0.8) {
    // 20% - Collection operations
    triggerAssetCollection();
    listAssets();
  } else {
    // 20% - Error scenarios
    testErrorHandling();
    healthCheck();
  }

  // Think time between requests
  sleep(Math.random() * 2 + 1);
}

// Setup function (runs once before the test)
export function setup() {
  console.log("Starting EstFor Asset Collection System Load Test");
  console.log(`Base URL: ${__ENV.BASE_URL || "http://localhost:8000"}`);
  console.log(`Test scenario: ${__ENV.SCENARIO || "load"}`);

  // Verify system is ready
  const healthResponse = http.get(
    `${__ENV.BASE_URL || "http://localhost:8000"}/health`
  );
  if (healthResponse.status !== 200) {
    throw new Error("System is not ready for testing");
  }

  console.log("System is ready for load testing");
}

// Teardown function (runs once after the test)
export function teardown(data) {
  console.log("Load test completed");
  console.log(`Total assets created: ${assetCount}`);
  console.log(`Average asset creation time: ${assetCreationTime.mean}ms`);
  console.log(`Average asset retrieval time: ${assetRetrievalTime.mean}ms`);
  console.log(`Average health check time: ${healthCheckTime.mean}ms`);
  console.log(`Error rate: ${errorRate.rate}`);
}

// Handle test results
export function handleSummary(data) {
  return {
    "load-test-results.json": JSON.stringify(data, null, 2),
    stdout: `
    EstFor Asset Collection System - Load Test Results
    =================================================
    
    Test Configuration:
    - Scenario: ${__ENV.SCENARIO || "load"}
    - Duration: ${data.state.testRunDuration}ms
    - Virtual Users: ${data.metrics.vus?.value || "N/A"}
    
    Performance Metrics:
    - HTTP Request Duration (95th percentile): ${
      data.metrics.http_req_duration?.values?.p95 || "N/A"
    }ms
    - HTTP Request Rate: ${data.metrics.http_reqs?.rate || "N/A"} req/s
    - Error Rate: ${data.metrics.errors?.rate || "N/A"}%
    
    Custom Metrics:
    - Assets Created: ${data.metrics.assets_created?.count || "N/A"}
    - Average Asset Creation Time: ${
      data.metrics.asset_creation_time?.avg || "N/A"
    }ms
    - Average Asset Retrieval Time: ${
      data.metrics.asset_retrieval_time?.avg || "N/A"
    }ms
    - Average Health Check Time: ${
      data.metrics.health_check_time?.avg || "N/A"
    }ms
    
    Threshold Results:
    ${Object.entries(data.thresholds || {})
      .map(([name, result]) => `- ${name}: ${result.ok ? "PASS" : "FAIL"}`)
      .join("\n")}
    `,
  };
}
