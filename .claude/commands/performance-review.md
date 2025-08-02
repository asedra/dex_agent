---
description: "Performance analysis and optimization recommendations"
shortcut: "pr"
---

# Performance Review

Comprehensive performance analysis and optimization recommendations for your application.

## System Resource Analysis

### Memory Usage
!`echo "💾 Memory analysis:"`
!`if command -v free >/dev/null 2>&1; then
    free -h | grep -E "Mem:|Swap:"
elif command -v vm_stat >/dev/null 2>&1; then
    vm_stat | head -5
else
    echo "  Memory stats not available"
fi`

### CPU Usage
!`echo "⚡ CPU analysis:"`
!`if command -v top >/dev/null 2>&1; then
    top -bn1 | grep "Cpu(s)" || echo "  CPU stats not available"
elif command -v htop >/dev/null 2>&1; then
    echo "  htop available for detailed analysis"
else
    echo "  CPU monitoring tools not available"
fi`

## Application Performance

### Bundle Size Analysis
!`if [ -f "package.json" ]; then
    echo "📦 Bundle size analysis:"
    
    # Check if build directory exists
    if [ -d "build" ] || [ -d "dist" ]; then
        build_dir=$([ -d "build" ] && echo "build" || echo "dist")
        echo "📊 Build output size:"
        du -sh "$build_dir" 2>/dev/null || echo "  Build directory analysis failed"
        
        echo "📁 Large files in build:"
        find "$build_dir" -type f -size +100k 2>/dev/null | head -5 | while read file; do
            size=$(du -h "$file" | cut -f1)
            echo "  $size - $(basename "$file")"
        done
    else
        echo "💡 No build directory found - run build process first"
    fi
    
    # Check for webpack-bundle-analyzer
    if grep -q webpack-bundle-analyzer package.json; then
        echo "✅ webpack-bundle-analyzer available for detailed analysis"
    else
        echo "💡 Consider adding webpack-bundle-analyzer for bundle analysis"
    fi
else
    echo "💡 No package.json found"
fi`

### Dependency Performance
!`if [ -f "package.json" ]; then
    echo "📊 Dependency analysis:"
    
    # Count dependencies
    deps=$(grep -c "\".*\":" package.json 2>/dev/null || echo "0")
    echo "📈 Total dependencies in package.json: $deps"
    
    # Check for heavy dependencies
    echo "⚠️  Potentially heavy dependencies:"
    if grep -q "lodash\|moment\|rxjs\|three\|d3" package.json; then
        grep "lodash\|moment\|rxjs\|three\|d3" package.json | head -3
    else
        echo "  No obviously heavy dependencies detected"
    fi
    
    # Node modules size
    if [ -d "node_modules" ]; then
        node_modules_size=$(du -sh node_modules 2>/dev/null | cut -f1)
        echo "📁 node_modules size: $node_modules_size"
    fi
fi`

## Code Performance Analysis

### File Size Analysis
!`echo "📄 Source file analysis:"`
!`find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | head -10 | while read file; do
    lines=$(wc -l < "$file" 2>/dev/null)
    size=$(du -h "$file" 2>/dev/null | cut -f1)
    if [ "$lines" -gt 500 ]; then
        echo "⚠️  Large file: $file ($lines lines, $size)"
    elif [ "$lines" -gt 200 ]; then
        echo "💡 Medium file: $file ($lines lines, $size)"
    fi
done`

### Import Analysis
!`echo "📥 Import performance check:"`
!`if find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep "import.*{.*}" 2>/dev/null | head -5 | grep -q .; then
    echo "📊 Named imports detected (good for tree shaking):"
    find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep "import.*{.*}" 2>/dev/null | head -3
fi

if find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep "import.*\\*.*from" 2>/dev/null | head -1 | grep -q .; then
    echo "⚠️  Wildcard imports found (may impact performance):"
    find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep "import.*\\*.*from" 2>/dev/null | head -3
fi`

### Loop Performance
!`echo "🔄 Loop performance analysis:"`
!`loop_count=$(find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep -c "for\|while\|forEach\|map\|filter" 2>/dev/null | awk '{sum+=$1} END {print sum}')
echo "📊 Total loops/iterations: ${loop_count:-0}"

# Check for nested loops
if find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep -A5 -B5 "for.*for\|while.*while" 2>/dev/null | head -1 | grep -q .; then
    echo "⚠️  Nested loops detected - potential O(n²) complexity"
else
    echo "✅ No obvious nested loops detected"
fi`

## Database Performance

### Query Analysis
!`echo "🗄️  Database performance check:"`
!`if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -l "SELECT\|INSERT\|UPDATE\|DELETE" 2>/dev/null | head -1 | grep -q .; then
    echo "📊 Database queries detected:"
    
    # Check for SELECT *
    if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep "SELECT \\*" 2>/dev/null | head -1 | grep -q .; then
        echo "⚠️  SELECT * queries found - consider specific column selection"
    fi
    
    # Check for N+1 query patterns
    if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -A3 -B3 "forEach.*query\|map.*query" 2>/dev/null | head -1 | grep -q .; then
        echo "⚠️  Potential N+1 query pattern detected"
    fi
else
    echo "💡 No direct database queries detected"
fi`

## Web Performance

### Image Optimization
!`echo "🖼️  Image performance analysis:"`
!`image_count=$(find . -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.svg" | wc -l)
echo "📊 Total images: $image_count"

if [ "$image_count" -gt 0 ]; then
    echo "📁 Large images (>100KB):"
    find . -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -size +100k | head -5 | while read img; do
        size=$(du -h "$img" | cut -f1)
        echo "  $size - $(basename "$img")"
    done
    echo "💡 Consider image optimization and WebP format"
fi`

### CSS Performance
!`echo "🎨 CSS performance check:"`
!`css_files=$(find . -name "*.css" -o -name "*.scss" -o -name "*.sass" | wc -l)
echo "📊 CSS files: $css_files"

if [ "$css_files" -gt 0 ]; then
    # Check for large CSS files
    find . -name "*.css" -o -name "*.scss" -o -name "*.sass" | while read css; do
        lines=$(wc -l < "$css" 2>/dev/null)
        if [ "$lines" -gt 1000 ]; then
            echo "⚠️  Large CSS file: $(basename "$css") ($lines lines)"
        fi
    done
    
    # Check for unused CSS (basic check)
    if find . -name "*.css" | xargs grep -l "display: none\|visibility: hidden" 2>/dev/null | head -1 | grep -q .; then
        echo "💡 Hidden elements detected - consider removing unused CSS"
    fi
fi`

## Network Performance

### HTTP Requests
!`echo "🌐 Network performance analysis:"`
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -c "fetch\|axios\|XMLHttpRequest" 2>/dev/null | awk '{sum+=$1} END {print sum}' | grep -q .; then
    request_count=$(find . -name "*.js" -o -name "*.ts" | xargs grep -c "fetch\|axios\|XMLHttpRequest" 2>/dev/null | awk '{sum+=$1} END {print sum}')
    echo "📊 HTTP requests in code: $request_count"
    
    # Check for request optimization
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "Promise.all\|Promise.allSettled" 2>/dev/null | head -1 | grep -q .; then
        echo "✅ Parallel request optimization detected"
    else
        echo "💡 Consider batching or parallelizing HTTP requests"
    fi
else
    echo "💡 No HTTP requests detected in source code"
fi`

## Performance Metrics

### Build Performance
!`if [ -f "package.json" ]; then
    echo "⚡ Build performance check:"
    
    # Check build scripts
    if grep -q '"build"' package.json; then
        echo "✅ Build script configured"
    fi
    
    # Check for webpack
    if grep -q webpack package.json; then
        echo "📦 Webpack detected - check webpack.config.js for optimizations"
    fi
    
    # Check for production optimizations
    if grep -q "NODE_ENV.*production" package.json; then
        echo "✅ Production environment configuration found"
    fi
fi`

## Performance Recommendations

### High Priority (Critical Impact)
1. **Bundle Size Optimization**
   - Implement code splitting
   - Remove unused dependencies
   - Use tree shaking
   - Optimize images and assets

2. **Database Optimization**
   - Add database indexes
   - Optimize queries (avoid SELECT *)
   - Implement connection pooling
   - Cache frequently accessed data

3. **Memory Management**
   - Fix memory leaks
   - Optimize large data structures
   - Implement pagination for large datasets
   - Use lazy loading

### Medium Priority (Moderate Impact)
1. **Code Optimization**
   - Optimize loops and algorithms
   - Implement memoization
   - Reduce function call overhead
   - Optimize regular expressions

2. **Network Optimization**
   - Implement HTTP caching
   - Use CDN for static assets
   - Compress responses (gzip/brotli)
   - Minimize HTTP requests

3. **CSS/JS Optimization**
   - Minify and compress files
   - Remove unused CSS/JS
   - Implement lazy loading
   - Use efficient selectors

### Low Priority (Minor Impact)
1. **Monitoring & Analysis**
   - Add performance monitoring
   - Implement performance budgets
   - Regular performance audits
   - User experience metrics

## Performance Testing Tools

### Recommended Tools
- **Lighthouse**: Web performance auditing
- **WebPageTest**: Detailed performance analysis
- **webpack-bundle-analyzer**: Bundle size analysis
- **Chrome DevTools**: Runtime performance profiling

### Monitoring Solutions
- **New Relic**: Application performance monitoring
- **DataDog**: Infrastructure and application monitoring
- **Google Analytics**: User experience tracking
- **Sentry**: Error and performance monitoring

## Next Steps

1. **Profile Application**: Use browser dev tools to identify bottlenecks
2. **Optimize Critical Path**: Focus on largest performance impacts first
3. **Implement Monitoring**: Set up continuous performance monitoring
4. **Regular Audits**: Schedule periodic performance reviews
5. **Performance Budget**: Set and maintain performance budgets

Use `/run-tests` to verify performance optimizations don't break functionality and `/check-standards` for code quality maintenance.