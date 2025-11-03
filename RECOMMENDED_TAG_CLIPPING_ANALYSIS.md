# RECOMMENDED Tag Clipping Analysis

## **PROBLEM IDENTIFIED**

The "RECOMMENDED" tag on protection strategies for institutional is getting cut off/clipped.

---

## **ROOT CAUSE ANALYSIS**

### **Current Implementation:**

**CSS:**
```css
.strategy-option.recommended::before {
    content: "RECOMMENDED";
    position: absolute;
    top: -12px;  /* Positioned 12px ABOVE the card */
    left: 24px;
    background: var(--accent-primary);
    color: var(--bg-main);
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: none;
}
```

**Strategy Option:**
```css
.strategy-option {
    position: relative; /* Good - allows absolute positioning of ::before */
    /* ... other styles */
}
```

**Strategies Grid:**
```css
.strategies-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    margin-top: 40px;
    width: 100%;
    max-width: 100%;
    overflow-x: auto; /* ⚠️ POTENTIAL ISSUE */
}
```

---

## **WHY IT'S GETTING CUT OFF**

### **Primary Issue: Grid Gap Insufficient**

The tag is positioned `top: -12px` (12px above the card), but:

1. **Grid Gap is Only 16px:**
   - Tag extends 12px upward
   - Next card starts 16px below
   - Tag height ≈ 12px (font) + 12px (padding) = ~24-28px total
   - **Problem:** Tag extends beyond the 16px gap, getting clipped by next card or grid container

2. **Overflow-x: auto on Grid:**
   - While this is for horizontal scrolling, it could contribute to clipping
   - Grid containers can clip absolutely positioned children

3. **No Padding on Grid Container:**
   - The `.strategies-grid` has no top padding
   - First card's tag at `top: -12px` extends into negative space
   - May get clipped by parent container's overflow settings

4. **Container Overflow:**
   - Parent containers (`.strategy-content`, `.demo-workflow`) may have `overflow: hidden`
   - This would clip anything extending outside bounds

---

## **SOLUTIONS (Priority Order)**

### **SOLUTION 1: Increase Grid Gap** ⭐ **RECOMMENDED**

**Change:**
```css
.strategies-grid {
    gap: 32px; /* Increase from 16px to accommodate tag */
}
```

**Why:**
- Tag extends ~12px above + ~12px height = ~24px needed
- 32px gap provides safe space (8px buffer)
- Simple, clean fix
- Maintains visual spacing

**Risk:** 🟢 **LOW**
- Slightly more spacing between cards
- May need to adjust on mobile

**Files:** `static/style.css` line ~1391

---

### **SOLUTION 2: Add Top Padding to Grid Container**

**Change:**
```css
.strategies-grid {
    padding-top: 16px; /* Space for first card's tag */
}
```

**Why:**
- Provides space for first card's tag
- Doesn't affect gap between cards
- Clean solution

**Risk:** 🟢 **LOW**
- Adds minimal top spacing
- May need to adjust `margin-top` if already 40px

**Files:** `static/style.css` line ~1388

---

### **SOLUTION 3: Adjust Tag Position**

**Change:**
```css
.strategy-option.recommended::before {
    top: -8px; /* Reduce from -12px to -8px */
    /* OR */
    top: 0px; /* Position at top of card instead of above */
    transform: translateY(-50%); /* Center on top edge */
}
```

**Why:**
- Reduces overlap into negative space
- Less likely to get clipped
- Alternative: Position at top edge instead of above

**Risk:** 🟡 **MEDIUM**
- Changes visual appearance
- May not look as polished if positioned differently
- Less "badge" feel if at top edge

**Files:** `static/style.css` line ~1446

---

### **SOLUTION 4: Change Overflow on Grid Container**

**Change:**
```css
.strategies-grid {
    overflow-x: auto;
    overflow-y: visible; /* Allow vertical overflow for tag */
}
```

**Why:**
- Prevents horizontal overflow while allowing tag to show
- Maintains current spacing

**Risk:** 🟢 **LOW**
- Shouldn't affect layout
- May need to check parent containers too

**Files:** `static/style.css` line ~1395

---

### **SOLUTION 5: Add Padding-Top to First Strategy Card** ⭐ **BEST COMPREHENSIVE FIX**

**Change:**
```css
.strategies-grid {
    gap: 24px; /* Slightly increase from 16px */
    padding-top: 16px; /* Space for first tag */
}

/* OR use :first-child selector */
.strategies-grid .strategy-option:first-child {
    margin-top: 16px; /* Space for tag */
}
```

**Why:**
- Addresses both first card and gap issues
- Comprehensive solution
- Maintains visual consistency

**Risk:** 🟢 **LOW**
- Well-tested approach
- No visual disruption

**Files:** `static/style.css` line ~1388-1395

---

## **RECOMMENDED APPROACH**

### **Combination Solution (Best Fix):**

**1. Increase Grid Gap:**
```css
.strategies-grid {
    gap: 32px; /* From 16px - accommodates tag + breathing room */
}
```

**2. Add Top Padding:**
```css
.strategies-grid {
    padding-top: 16px; /* Space for first card's tag */
}
```

**3. Ensure Overflow Allows Vertical:**
```css
.strategies-grid {
    overflow-x: auto;
    overflow-y: visible; /* Explicitly allow vertical overflow */
}
```

**Why This Combination:**
- ✅ Addresses first card clipping (padding-top)
- ✅ Addresses gap between cards (increased gap)
- ✅ Ensures overflow doesn't clip tags
- ✅ Maintains visual consistency
- ✅ Low risk, easy to implement

---

## **ALTERNATIVE: Mobile Considerations**

### **If Issues on Mobile:**

```css
@media (max-width: 768px) {
    .strategies-grid {
        gap: 24px; /* Smaller gap on mobile if needed */
        padding-top: 12px; /* Smaller padding on mobile */
    }
    
    .strategy-option.recommended::before {
        top: -8px; /* Less overlap on mobile */
        font-size: 11px; /* Slightly smaller tag */
        padding: 4px 10px; /* Smaller padding */
    }
}
```

---

## **RISK ASSESSMENT**

### **Overall Risk: 🟢 LOW**

**Why:**
- All solutions are CSS-only
- No functionality changes
- Easy to test and revert
- Visual spacing adjustments only

**Potential Issues:**
1. **More spacing between cards** - May make list feel longer
   - **Mitigation:** 32px is still reasonable, maintains professional look

2. **Mobile layout** - May need responsive adjustments
   - **Mitigation:** Media queries can fine-tune

3. **Visual consistency** - Need to ensure matches other badges
   - **Mitigation:** Only affects spacing, not tag appearance

---

## **IMPLEMENTATION PLAN**

### **Phase 1: Primary Fix**
1. Increase `.strategies-grid` gap to 32px
2. Add `padding-top: 16px` to grid
3. Add `overflow-y: visible` to grid

### **Phase 2: Verify**
1. Test on desktop view
2. Test on mobile view
3. Check first card tag visibility
4. Check tags between cards

### **Phase 3: Fine-tune (if needed)**
1. Adjust gap if too much/little spacing
2. Adjust padding if needed
3. Mobile responsive adjustments if required

---

## **EXPECTED OUTCOME**

After implementation:
- ✅ "RECOMMENDED" tag fully visible on first card
- ✅ Tags between cards fully visible
- ✅ No clipping or cutoff
- ✅ Professional spacing maintained
- ✅ Works on all screen sizes

---

## **FILES TO MODIFY**

- `static/style.css`:
  - Line ~1388-1395: `.strategies-grid` styles
  - Line ~1443-1455: `.strategy-option.recommended::before` (optional adjustment)
  - Mobile media query: Add responsive adjustments if needed

---

**Status:** Ready for Implementation  
**Risk Level:** 🟢 LOW  
**Recommended Solution:** Combination of increased gap + padding-top

