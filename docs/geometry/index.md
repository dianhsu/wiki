---
comments: true
---
## Geometry

### 极角排序

```cpp

struct Point{
    ll x, y;
    Point() = default;
    Point(int argx, int argy): x(argx), y(argy){}
    bool up() const{
        return y > 0 or (y == 0 and x >= 0);
    }
};
ll det(const Point& a, const Point& b) {
    return a.x * b.y - b.x * a.y;
}
 
ll dot(const Point& a, const Point& b) {
    return a.x * b.x + a.y * b.y;
}
 
bool cmp(const Point& a, const Point& b) {
    if (a.up() ^ b.up()) return a.up() > b.up();
    return det(a, b) > 0;
}
 
bool same(const Point& a, const Point& b) {
    ll d = det (a, b);
    if (d > 0) return true;
    if (d < 0) return false;
    return dot (a, b) > 0;
}

```

### 凸包

```cpp
// 基本数据类型，面积和边长的数据
template<typename T, typename AFT>
class Andrew{
    typedef pair<T, T> PTT;
    PTT reduce(PTT a, PTT b){
        return PTT{a.first - b.first, a.second - b.second};
    }
    T cross(PTT a, PTT b){
        return a.first * b.second - a.second * b.first;
    }
    T area(PTT a, PTT b, PTT c){
        return cross(reduce(b , a), reduce(c , a));
    }
    AFT dist(PTT a, PTT b){
        AFT dx = a.first - b.first;
        AFT dy = a.second - b.second;
        return sqrt(dx * dx + dy * dy);
    }
public:
    Andrew()= default;
    Andrew(const vector<PTT>& argv): vec(argv){}
    void addPoint(PTT p){
        vec.push_back(p);
    }
    // 边长， 面积， 按节点顺序的边缘节点序列（第一个点和最后一个点是一样的）
    // 注意：如果考虑凸包上点的数目最少，需要将while循环允许面积等于0
    tuple<T, T, vector<PTT>> run(){
        sort(vec.begin(), vec.end());
        vector<int> st;
        // vis是用来记录第一遍访问的节点，而不是最终在凸包上面的点
        vector<bool> vis(vec.size(), false);
        for(int i = 0; i < vec.size(); ++i){
            while(st.size() >= 2 and area(vec[*next(st.rbegin(), 1)], vec[*st.rbegin()], vec[i]) < 0){
                if(area(vec[*next(st.rbegin(), 1)], vec[*st.rbegin()], vec[i]) < 0){
                    vis[st.back()] = false;
                }
                st.pop_back();
            }
            st.push_back(i);
            vis[st.back()] = true;
        }
        vis[0] = false;
        for(int i = (int)vec.size() - 1; i >= 0; --i){
            if(vis[i]) continue;
            while(st.size() >= 2 and area(vec[*next(st.rbegin(), 1)], vec[*st.rbegin()], vec[i]) < 0){
                st.pop_back();
            }
            st.push_back(i);
        }
        AFT dis = 0;
        AFT ars = 0;
        vector<PTT> res;
        for(auto& it: st) res.push_back(vec[it]);
        for(int i = 1; i < st.size(); ++i){
            dis += dist(vec[st[i - 1]], vec[st[i]]);
            ars += area(vec[0], vec[st[i - 1]], vec[st[i]]);
        }
        return {dis, ars, res};
    }
private:
    vector<PTT> vec;
};

```

### 方阵的三维操作模板
> 翻转，旋转和转置
```cpp
class Rectangle{
public:
    typedef pair<int, int> Point;
    Rectangle(int sx, int sy) : dx({1, 0}), dy({0, 1}), vec({Point{0, 0}, Point{0, sy - 1}, Point{sx - 1, 0}, Point{sx - 1, sy - 1}}){}
    void mirror(int dr = 1){
        if(dr == 1){
            // 沿着x轴翻转
            swap(vec[0], vec[1]);
            swap(vec[2], vec[3]);
        }else{
            // 沿着y轴翻转
            swap(vec[0], vec[2]);
            swap(vec[1], vec[3]);
        }
        update();
    }
    void transpose(int dr = 1){
        if(dr == 1){
            // 沿着y = x 翻转
            swap(vec[1], vec[2]);
        }else{
            // 沿着x + y = n 翻转
            swap(vec[0], vec[3]);
        }
        update();
    }
    void rotate(int dr = 1){
        transpose();
        if(dr == 1){
            // 顺时针
            mirror(1);
        }else{
            // 逆时针
            mirror(0);
        }
        update();
    }
    Point mapping(Point p){
        return {vec[0].first + dx.first * p.first + dy.first * p.second, vec[0].second + dx.second * p.first + dy.second * p.second};
    }
    Point dx, dy;
    array<Point, 4> vec;
private:
    void update(){
        int xlim = abs(vec[2].first - vec[0].first) + abs(vec[2].second - vec[0].second);
        int ylim = abs(vec[1].first - vec[0].first) + abs(vec[1].second - vec[0].second);
        assert(xlim > 0 and ylim > 0);
        dx = Point{(vec[2].first - vec[0].first) / xlim, (vec[2].second - vec[0].second) / xlim};
        dy = Point{(vec[1].first - vec[0].first) / ylim, (vec[1].second - vec[0].second) / ylim};
    }
};
```
