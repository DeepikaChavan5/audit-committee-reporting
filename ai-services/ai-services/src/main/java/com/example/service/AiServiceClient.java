package com.example.service;

import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class AiServiceClient {

    private final RestTemplate restTemplate;
    private final String BASE_URL = "http://localhost:5000";

    // 🔹 Constructor
    public AiServiceClient() {
        this.restTemplate = createRestTemplateWithTimeout();
    }

    // 🔹 Configure 10 seconds timeout
    private RestTemplate createRestTemplateWithTimeout() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(10000); // 10 sec
        factory.setReadTimeout(10000);    // 10 sec
        return new RestTemplate(factory);
    }

    // 🔹 Generic GET method
    public String getRequest(String endpoint) {
        try {
            String url = BASE_URL + endpoint;
            ResponseEntity<String> response =
                    restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            System.out.println("GET Error: " + e.getMessage());
            return null; // graceful handling
        }
    }

    // 🔹 Generic POST method
    public String postRequest(String endpoint, Object requestBody) {
        try {
            String url = BASE_URL + endpoint;
            ResponseEntity<String> response =
                    restTemplate.postForEntity(url, requestBody, String.class);
            return response.getBody();
        } catch (Exception e) {
            System.out.println("POST Error: " + e.getMessage());
            return null; // graceful handling
        }
    }

    // 🔹 Chat API
    public String getChatResponse(Object requestBody) {
        return postRequest("/chat", requestBody);
    }

    // 🔹 Summarize API
    public String getSummary(Object requestBody) {
        return postRequest("/summarize", requestBody);
    }

    // 🔹 Generate Report API
    public String generateReport(Object requestBody) {
        return postRequest("/generate-report", requestBody);
    }

    // 🔹 Health Check API
    public String checkHealth() {
        return getRequest("/health");
    }
}