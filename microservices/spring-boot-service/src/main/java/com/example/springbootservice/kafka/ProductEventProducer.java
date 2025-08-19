package com.example.springbootservice.kafka;

import com.example.springbootservice.dto.ProductDto;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;

import java.util.concurrent.CompletableFuture;

@Component
public class ProductEventProducer {
    
    private static final Logger logger = LoggerFactory.getLogger(ProductEventProducer.class);
    
    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    private static final String PRODUCT_EVENTS_TOPIC = "product_events";
    private static final String PRODUCT_UPDATES_TOPIC = "product_updates";
    
    /**
     * Send product created event
     */
    public CompletableFuture<SendResult<String, Object>> sendProductCreatedEvent(ProductDto product) {
        ProductEvent event = new ProductEvent();
        event.setEventType("PRODUCT_CREATED");
        event.setProductId(product.getId());
        event.setProductName(product.getName());
        event.setTimestamp(System.currentTimeMillis());
        event.setData(product);
        
        return sendEvent(PRODUCT_EVENTS_TOPIC, event);
    }
    
    /**
     * Send product updated event
     */
    public CompletableFuture<SendResult<String, Object>> sendProductUpdatedEvent(ProductDto product) {
        ProductEvent event = new ProductEvent();
        event.setEventType("PRODUCT_UPDATED");
        event.setProductId(product.getId());
        event.setProductName(product.getName());
        event.setTimestamp(System.currentTimeMillis());
        event.setData(product);
        
        return sendEvent(PRODUCT_UPDATES_TOPIC, event);
    }
    
    /**
     * Send product deleted event
     */
    public CompletableFuture<SendResult<String, Object>> sendProductDeletedEvent(Long productId, String productName) {
        ProductEvent event = new ProductEvent();
        event.setEventType("PRODUCT_DELETED");
        event.setProductId(productId);
        event.setProductName(productName);
        event.setTimestamp(System.currentTimeMillis());
        
        return sendEvent(PRODUCT_EVENTS_TOPIC, event);
    }
    
    /**
     * Send stock updated event
     */
    public CompletableFuture<SendResult<String, Object>> sendStockUpdatedEvent(Long productId, String productName, Integer newStock) {
        ProductEvent event = new ProductEvent();
        event.setEventType("STOCK_UPDATED");
        event.setProductId(productId);
        event.setProductName(productName);
        event.setTimestamp(System.currentTimeMillis());
        event.setData(new StockUpdateData(newStock));
        
        return sendEvent(PRODUCT_UPDATES_TOPIC, event);
    }
    
    /**
     * Send low stock alert
     */
    public CompletableFuture<SendResult<String, Object>> sendLowStockAlert(Long productId, String productName, Integer currentStock) {
        ProductEvent event = new ProductEvent();
        event.setEventType("LOW_STOCK_ALERT");
        event.setProductId(productId);
        event.setProductName(productName);
        event.setTimestamp(System.currentTimeMillis());
        event.setData(new StockUpdateData(currentStock));
        
        return sendEvent("low_stock_alerts", event);
    }
    
    /**
     * Generic method to send events
     */
    private CompletableFuture<SendResult<String, Object>> sendEvent(String topic, ProductEvent event) {
        String key = event.getProductId() != null ? event.getProductId().toString() : "system";
        
        CompletableFuture<SendResult<String, Object>> future = kafkaTemplate.send(topic, key, event);
        
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                logger.info("Event sent successfully to topic: {}, partition: {}, offset: {}", 
                    topic, result.getRecordMetadata().partition(), result.getRecordMetadata().offset());
            } else {
                logger.error("Failed to send event to topic: {}", topic, ex);
            }
        });
        
        return future;
    }
    
    // Event classes
    public static class ProductEvent {
        private String eventType;
        private Long productId;
        private String productName;
        private Long timestamp;
        private Object data;
        
        // Getters and Setters
        public String getEventType() { return eventType; }
        public void setEventType(String eventType) { this.eventType = eventType; }
        
        public Long getProductId() { return productId; }
        public void setProductId(Long productId) { this.productId = productId; }
        
        public String getProductName() { return productName; }
        public void setProductName(String productName) { this.productName = productName; }
        
        public Long getTimestamp() { return timestamp; }
        public void setTimestamp(Long timestamp) { this.timestamp = timestamp; }
        
        public Object getData() { return data; }
        public void setData(Object data) { this.data = data; }
    }
    
    public static class StockUpdateData {
        private Integer stockQuantity;
        
        public StockUpdateData() {}
        
        public StockUpdateData(Integer stockQuantity) {
            this.stockQuantity = stockQuantity;
        }
        
        public Integer getStockQuantity() { return stockQuantity; }
        public void setStockQuantity(Integer stockQuantity) { this.stockQuantity = stockQuantity; }
    }
}
