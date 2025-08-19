package com.example.springbootservice.repository;

import com.example.springbootservice.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    /**
     * Find products by name (case-insensitive)
     */
    List<Product> findByNameContainingIgnoreCase(String name);
    
    /**
     * Find products by price range
     */
    List<Product> findByPriceBetween(BigDecimal minPrice, BigDecimal maxPrice);
    
    /**
     * Find products with stock quantity greater than specified value
     */
    List<Product> findByStockQuantityGreaterThan(Integer minStock);
    
    /**
     * Find products by name using custom query
     */
    @Query("SELECT p FROM Product p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Product> findProductsByNameLike(@Param("name") String name);
    
    /**
     * Find products with low stock (less than specified quantity)
     */
    @Query("SELECT p FROM Product p WHERE p.stockQuantity < :maxStock")
    List<Product> findProductsWithLowStock(@Param("maxStock") Integer maxStock);
    
    /**
     * Find product by name (exact match)
     */
    Optional<Product> findByName(String name);
    
    /**
     * Check if product exists by name
     */
    boolean existsByName(String name);
}
