package com.example.springbootservice.service;

import com.example.springbootservice.dto.ProductDto;
import com.example.springbootservice.kafka.ProductEventProducer;
import com.example.springbootservice.model.Product;
import com.example.springbootservice.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@Transactional
public class ProductService {
    
    @Autowired
    private ProductRepository productRepository;
    
    @Autowired
    private ProductEventProducer productEventProducer;
    
    /**
     * Create a new product
     */
    public ProductDto createProduct(ProductDto productDto) {
        Product product = new Product();
        product.setName(productDto.getName());
        product.setDescription(productDto.getDescription());
        product.setPrice(productDto.getPrice());
        product.setStockQuantity(productDto.getStockQuantity() != null ? productDto.getStockQuantity() : 0);
        
        Product savedProduct = productRepository.save(product);
        ProductDto savedProductDto = convertToDto(savedProduct);
        
        // Send Kafka event
        productEventProducer.sendProductCreatedEvent(savedProductDto);
        
        return savedProductDto;
    }
    
    /**
     * Get product by ID
     */
    @Cacheable(value = "products", key = "#id")
    public Optional<ProductDto> getProductById(Long id) {
        return productRepository.findById(id)
                .map(this::convertToDto);
    }
    
    /**
     * Get all products with pagination
     */
    @Cacheable(value = "products", key = "'all'")
    public Page<ProductDto> getAllProducts(Pageable pageable) {
        return productRepository.findAll(pageable)
                .map(this::convertToDto);
    }
    
    /**
     * Get all products
     */
    @Cacheable(value = "products", key = "'list'")
    public List<ProductDto> getAllProducts() {
        return productRepository.findAll()
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    /**
     * Update product
     */
    @CacheEvict(value = "products", key = "#id")
    public Optional<ProductDto> updateProduct(Long id, ProductDto productDto) {
        return productRepository.findById(id)
                .map(product -> {
                    if (productDto.getName() != null) {
                        product.setName(productDto.getName());
                    }
                    if (productDto.getDescription() != null) {
                        product.setDescription(productDto.getDescription());
                    }
                    if (productDto.getPrice() != null) {
                        product.setPrice(productDto.getPrice());
                    }
                    if (productDto.getStockQuantity() != null) {
                        product.setStockQuantity(productDto.getStockQuantity());
                    }
                    
                    Product savedProduct = productRepository.save(product);
                    ProductDto savedProductDto = convertToDto(savedProduct);
                    
                    // Send Kafka event
                    productEventProducer.sendProductUpdatedEvent(savedProductDto);
                    
                    return savedProductDto;
                });
    }
    
    /**
     * Delete product
     */
    @CacheEvict(value = "products", key = "#id")
    public boolean deleteProduct(Long id) {
        return productRepository.findById(id)
                .map(product -> {
                    String productName = product.getName();
                    productRepository.deleteById(id);
                    
                    // Send Kafka event
                    productEventProducer.sendProductDeletedEvent(id, productName);
                    
                    return true;
                })
                .orElse(false);
    }
    
    /**
     * Search products by name
     */
    public List<ProductDto> searchProductsByName(String name) {
        return productRepository.findByNameContainingIgnoreCase(name)
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    /**
     * Get products by price range
     */
    public List<ProductDto> getProductsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return productRepository.findByPriceBetween(minPrice, maxPrice)
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    /**
     * Get products with stock above threshold
     */
    public List<ProductDto> getProductsInStock(Integer minStock) {
        return productRepository.findByStockQuantityGreaterThan(minStock)
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    /**
     * Get products with low stock
     */
    public List<ProductDto> getProductsWithLowStock(Integer maxStock) {
        return productRepository.findProductsWithLowStock(maxStock)
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    /**
     * Update product stock quantity
     */
    @CacheEvict(value = "products", key = "#id")
    public Optional<ProductDto> updateStockQuantity(Long id, Integer newQuantity) {
        return productRepository.findById(id)
                .map(product -> {
                    product.setStockQuantity(newQuantity);
                    Product savedProduct = productRepository.save(product);
                    return convertToDto(savedProduct);
                });
    }
    
    /**
     * Check if product exists
     */
    public boolean productExists(Long id) {
        return productRepository.existsById(id);
    }
    
    /**
     * Check if product exists by name
     */
    public boolean productExistsByName(String name) {
        return productRepository.existsByName(name);
    }
    
    /**
     * Convert Product entity to ProductDto
     */
    private ProductDto convertToDto(Product product) {
        ProductDto dto = new ProductDto();
        dto.setId(product.getId());
        dto.setName(product.getName());
        dto.setDescription(product.getDescription());
        dto.setPrice(product.getPrice());
        dto.setStockQuantity(product.getStockQuantity());
        dto.setCreatedAt(product.getCreatedAt());
        dto.setUpdatedAt(product.getUpdatedAt());
        return dto;
    }
}
