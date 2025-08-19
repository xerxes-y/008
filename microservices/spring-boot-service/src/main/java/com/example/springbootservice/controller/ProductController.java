package com.example.springbootservice.controller;

import com.example.springbootservice.dto.ProductDto;
import com.example.springbootservice.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/products")
@Tag(name = "Product Management", description = "APIs for managing products")
public class ProductController {
    
    @Autowired
    private ProductService productService;
    
    @PostMapping
    @Operation(summary = "Create a new product", description = "Creates a new product with the provided details")
    public ResponseEntity<ProductDto> createProduct(@Valid @RequestBody ProductDto productDto) {
        ProductDto createdProduct = productService.createProduct(productDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdProduct);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get product by ID", description = "Retrieves a product by its ID")
    public ResponseEntity<ProductDto> getProductById(
            @Parameter(description = "Product ID") @PathVariable Long id) {
        Optional<ProductDto> product = productService.getProductById(id);
        return product.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping
    @Operation(summary = "Get all products", description = "Retrieves all products with optional pagination")
    public ResponseEntity<List<ProductDto>> getAllProducts(
            @Parameter(description = "Page number (0-based)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size") @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<ProductDto> products = productService.getAllProducts(pageable);
        return ResponseEntity.ok(products.getContent());
    }
    
    @GetMapping("/list")
    @Operation(summary = "Get all products without pagination", description = "Retrieves all products in a single list")
    public ResponseEntity<List<ProductDto>> getAllProductsList() {
        List<ProductDto> products = productService.getAllProducts();
        return ResponseEntity.ok(products);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update product", description = "Updates an existing product")
    public ResponseEntity<ProductDto> updateProduct(
            @Parameter(description = "Product ID") @PathVariable Long id,
            @Valid @RequestBody ProductDto productDto) {
        Optional<ProductDto> updatedProduct = productService.updateProduct(id, productDto);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete product", description = "Deletes a product by its ID")
    public ResponseEntity<Void> deleteProduct(
            @Parameter(description = "Product ID") @PathVariable Long id) {
        boolean deleted = productService.deleteProduct(id);
        return deleted ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }
    
    @GetMapping("/search")
    @Operation(summary = "Search products by name", description = "Searches products by name (case-insensitive)")
    public ResponseEntity<List<ProductDto>> searchProductsByName(
            @Parameter(description = "Product name to search for") @RequestParam String name) {
        List<ProductDto> products = productService.searchProductsByName(name);
        return ResponseEntity.ok(products);
    }
    
    @GetMapping("/price-range")
    @Operation(summary = "Get products by price range", description = "Retrieves products within a specified price range")
    public ResponseEntity<List<ProductDto>> getProductsByPriceRange(
            @Parameter(description = "Minimum price") @RequestParam BigDecimal minPrice,
            @Parameter(description = "Maximum price") @RequestParam BigDecimal maxPrice) {
        List<ProductDto> products = productService.getProductsByPriceRange(minPrice, maxPrice);
        return ResponseEntity.ok(products);
    }
    
    @GetMapping("/in-stock")
    @Operation(summary = "Get products in stock", description = "Retrieves products with stock quantity above threshold")
    public ResponseEntity<List<ProductDto>> getProductsInStock(
            @Parameter(description = "Minimum stock quantity") @RequestParam(defaultValue = "0") Integer minStock) {
        List<ProductDto> products = productService.getProductsInStock(minStock);
        return ResponseEntity.ok(products);
    }
    
    @GetMapping("/low-stock")
    @Operation(summary = "Get products with low stock", description = "Retrieves products with stock quantity below threshold")
    public ResponseEntity<List<ProductDto>> getProductsWithLowStock(
            @Parameter(description = "Maximum stock quantity") @RequestParam(defaultValue = "10") Integer maxStock) {
        List<ProductDto> products = productService.getProductsWithLowStock(maxStock);
        return ResponseEntity.ok(products);
    }
    
    @PatchMapping("/{id}/stock")
    @Operation(summary = "Update product stock quantity", description = "Updates the stock quantity of a product")
    public ResponseEntity<ProductDto> updateStockQuantity(
            @Parameter(description = "Product ID") @PathVariable Long id,
            @Parameter(description = "New stock quantity") @RequestParam Integer quantity) {
        Optional<ProductDto> updatedProduct = productService.updateStockQuantity(id, quantity);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping("/{id}/exists")
    @Operation(summary = "Check if product exists", description = "Checks if a product exists by ID")
    public ResponseEntity<Boolean> productExists(
            @Parameter(description = "Product ID") @PathVariable Long id) {
        boolean exists = productService.productExists(id);
        return ResponseEntity.ok(exists);
    }
    
    @GetMapping("/check-name")
    @Operation(summary = "Check if product exists by name", description = "Checks if a product exists by name")
    public ResponseEntity<Boolean> productExistsByName(
            @Parameter(description = "Product name") @RequestParam String name) {
        boolean exists = productService.productExistsByName(name);
        return ResponseEntity.ok(exists);
    }
}
