---
comments: true
---

## Fast I/O
```cpp
template<typename T = int>
inline T fRead() {
    T x = 0, w = 1; char c = getchar();
    while (c < '0' || c>'9') { if (c == '-') w = -1; c = getchar(); }
    while (c <= '9' && c >= '0') { x = (x << 1) + (x << 3) + c - '0'; c = getchar(); }
    return w == 1 ? x : -x;
}
template<typename T = int>
inline T cRead() {
    T ret;
    cin >> ret;
    return ret;
}
template<typename T = int>
inline void fWrite(T x){
    if(x < 0){
        x = -x;
        putchar('-');
    }
    if(x >= 10) fWrite(x / 10);
    putchar(x % 10 + '0');
}
template<typename T = int>
inline void cWrite(T x){
    cout << x;
}
```
## Y combinator

```cpp
template<class Fun>
class Y_combinator {
private:
    Fun fun_;
public:
    template<class F>
    Y_combinator(F&& fun) : fun_(static_cast<F&&>(fun)) {}
    template<class... Args>
    decltype(auto) operator () (Args&&...args) const {
        return fun_(*this, static_cast<Args&&>(args)...);
    }
};
template<class T> Y_combinator(T)->Y_combinator<T>;
```
## Numeric Binary Search
```cpp
int lower_bound(int target, vector<int>& vec){
    int pos = -1;
    for(int i = (32 - __builtin_clz(vec.size())); i; i >>= 1){
        if(pos + i < vec.size() and vec[pos + i] < target){
            pos += i;
        }
    }
    return pos + 1;
}
```
## Least Power of 2 and Greater Power of 2
```cpp
int leastPowerOfTwo(int val){
    return 32 - __builtin_clz(val - 1);
}
int greaterPowerOfTwo(int val){
    return 32 - __builtin_clz(val);
}
```