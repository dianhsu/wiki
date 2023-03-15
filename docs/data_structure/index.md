---
comments: true
---
## 数据结构
### 线段树

```cpp
// Luogu P3373
template<typename T = int>
inline T read() {
    T ret;
    cin >> ret;
    return ret;
}

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

#define MID ((l + r) >> 1)
#define LEFT (cur << 1)
#define RIGHT ((cur << 1) | 1)

int main(int argc, char* argv[]) {
    fastIO();
    int n, m;
    cin >> n >> m;
    vector<ll> arr{0};
    for (int i = 0; i < n; ++i) {
        arr.push_back(read<ll>());
    }
    vector<ll> lazy((n << 2) + 10);
    vector<ll> node((n << 2) + 10);
    Y_combinator(
        [&](auto&& build, int cur, int l, int r) -> void {
            if (l == r) {
                node[cur] = arr[l];
            } else {
                build(LEFT, l, MID);
                build(RIGHT, MID + 1, r);
                node[cur] = node[LEFT] + node[RIGHT];
            }
        }
    )(1, 1, n);
    auto&& lazyUpdate = [&](int cur, int l, int r) -> void {
        if (lazy[cur] != 0) {
            node[LEFT] += lazy[cur] * (MID - l + 1);
            node[RIGHT] += lazy[cur] * (r - MID);
            lazy[LEFT] += lazy[cur];
            lazy[RIGHT] += lazy[cur];
            lazy[cur] = 0;
        }
    };
    auto&& update = Y_combinator(
        [&](auto&& update, int cur, int l, int r, int s, int e, ll v) {
            if (s > r or e < l) return;
            if (s <= l and r <= e) {
                node[cur] += (r - l + 1) * v;
                lazy[cur] += v;
            } else {
                lazyUpdate(cur, l, r);
                update(LEFT, l, MID, s, e, v);
                update(RIGHT, MID + 1, r, s, e, v);
                node[cur] = node[LEFT] + node[RIGHT];
            }
        }
    );
    auto&& query = Y_combinator(
        [&](auto&& query, int cur, int l, int r, int s, int e)->ll {
            if (s > r or e < l) return 0;
            if (s <= l and e >= r) {
                return node[cur];
            }
            lazyUpdate(cur, l, r);
            ll ret = query(LEFT, l, MID, s, e);
            ret += query(RIGHT, MID + 1, r, s, e);
            return ret;
        }
    );
    while (m--) {
        int q, x, y, k;
        cin >> q >> x >> y;
        if (q == 1) {
            cin >> k;
            update(1, 1, n, x, y, k);
        } else {
            cout << query(1, 1, n, x, y) << endl;
        }
    }
    return 0;
}
```

### ST表（稀疏表）(C++17)

```cpp
template<typename iter, typename BinOp>
class SparseTable {
    using T = typename remove_reference<decltype(*declval<iter>())>::type;
    vector<vector<T>> arr;
    BinOp binOp;
public:
    SparseTable(iter begin, iter end, BinOp binOp) : arr(1), binOp(binOp) {
        int n = distance(begin, end);
        arr.assign(32 - __builtin_clz(n), vector<T>(n));
        arr[0].assign(begin, end);
        for (int i = 1; i < arr.size(); ++i) {
            for (int j = 0; j < n - (1 << i) + 1; ++j) {
                arr[i][j] = binOp(arr[i - 1][j], arr[i - 1][j + (1 << (i - 1))]);
            }
        }
    }
    T query(int lPos, int rPos) {
        int h = floor(log2(rPos - lPos + 1));
        return binOp(arr[h][lPos], arr[h][rPos - (1 << h) + 1]);
    }
};
```

### 树状数组

```cpp
template<typename T>
struct FenWick {
    int N;
    vector<T> arr;
    FenWick(int sz): N(sz), arr(sz + 1, 0) {}
    void update(int pos, T val) {
        for (; pos <= N;pos |= (pos + 1)) {
            arr[pos] += val;
        }
    }
    // 获取 [1, pos] 的和
    T get(int pos) {
        T ret = 0;
        for (; pos > 0; --pos) {
            ret += arr[pos];
            pos &= (pos + 1);
        }
        return ret;
    }
    // 获取 [l, r] 的和
    T query(int l, int r) {
        return get(r) - get(l - 1);
    }
};
```
### 珂朵莉树
```cpp
namespace Chtholly{
struct Node{
    int l, r;
    mutable int v;
    Node(int il, int ir, int iv): l(il), r(ir), v(iv){}
    bool operator < (const Node& arg) const{
        return l < arg.l;
    }
};
class Tree{
protected:
    auto split(int pos){
        if(pos > _sz) return odt.end();
        auto it = --odt.upper_bound(Node{pos, 0, 0});
        if(it->l == pos) return it;
        auto tmp = *it;
        odt.erase(it);
        odt.insert({tmp.l, pos - 1, tmp.v});
        return odt.insert({pos, tmp.r, tmp.v}).first;
    }  
public:
    Tree(int sz, int ini = 1): _sz(sz), odt({Node{1, sz, ini}}) {}
    virtual void assign(int l, int r, int v){
        auto itr = split(r + 1), itl = split(l);
        // operations here
        odt.erase(itl, itr);
        odt.insert({l, r, v});
    }
protected:
    int _sz;
    set<Node> odt;
};
}

```

### Splay树
> https://loj.ac/p/104
> 有误，暂未修

```cpp
#include <vector>
#include <array>
#include <iostream>
#include <cassert>
using namespace std;
template<typename T>
class SplayTree{
public:
    struct Node{
        Node *parent{};
        std::array<Node*, 2> child{};
        T val;
        // cnt: repeat of current element, sz: element count of child tree, sum: repeats of child tree
        size_t cnt, sz, sum;
        explicit Node(T value_arg): val(value_arg), cnt(1), sz(1), sum(1){}
        bool side() const{
            return parent->child[1] == this;
        }
        // maintain information of current element
        void maintain(){
            if(!this) return;
            this->sum = this->cnt;
            this->sz = 1;
            if(this->child[0]) {
                this->sum += this->child[0]->sum;
                this->sz += this->child[0]->sz;
            }
            if(this->child[1]) {
                this->sum += this->child[1]->sum;
                this->sz += this->child[1]->sz;
            }
        }
        // left rotate and right rotate
        void rotate(){
            const auto p = parent;
            const bool i = side();
            if(p->parent){
                p->parent->attach(p->side(), this);
            }else{
                parent = nullptr;
            }
            p->attach(i, child[!i]);
            attach(!i, p);
            p->maintain();
            maintain();
        }
        void splay(){
            for(;parent;rotate()){
                if(parent->parent){
                    (side() == parent->side() ? parent: this)->rotate();
                }
            }
        }
        // attach node new_ as the node's side child
        void attach(bool side, Node* const new_){
            if(new_) new_->parent = this;
            child[side] = new_;
        }
    };
    struct iterator{
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = T;
        using pointer = T*;
        using reference = T&;
        using difference_type = long long;
    public:
        Node* node;
        void operator--(){ advance<false>();}
        void operator++(){ advance<true>();}
        const T& operator*(){return node->val;}
        explicit iterator(Node* node_arg): node(node_arg){}
        bool operator==(const iterator oth) const{
            return node == oth.node;
        }
        bool operator != (const iterator oth) const{
            return *this != oth;
        }
    private:
        template<bool dir> void advance(){
            if(node->child[dir]){
                node = extremum<!dir>(node->child[dir]);
                return;
            }
            for(;node->parent and node->side() == dir; node = node->parent);
            node = node->parent;
        }
    };

    template<bool i> static Node* extremum(Node* x){
        assert(x);
        for(;x->child[i]; x = x->child[i]);
        return x;
    }
    Node* rt{};
    explicit SplayTree()= default;
    ~SplayTree(){ destroy(rt);}
    void insert(const T& arg){
        if(!rt){
            rt = new Node(arg);
            rt->maintain();
            return;
        }
        Node* cur = rt, *f = nullptr;
        while(true){
            if(cur->val == arg){
                cur->cnt++;
                cur->maintain();
                f->maintain();
                cur->splay();
                rt = cur;
                break;
            }
            f = cur;
            cur = cur->child[cur->val < arg];
            if(!cur){
                Node* tmp = new Node(arg);
                f->child[f->val < arg] = tmp;
                tmp->parent = f;
                tmp->maintain();
                f->maintain();
                tmp->splay();
                rt = tmp;
                break;
            }
        }
    }

    // size, sum
    std::pair<size_t, size_t> rank(const T& arg){
        std::pair<size_t, size_t> res{0, 0};
        Node* cur = rt;
        while(cur){
            if(arg < cur->val){
                cur = cur->child[0];
            }else{
                if(cur->child[0]) {
                    res.first += cur->child[0]->sz;
                    res.second += cur->child[0]->sum;
                }
                res.first ++;
                res.second += cur->cnt;
                if(arg == cur->val){
                    cur->splay();
                    rt = cur;
                    break;
                }
                cur = cur->child[1];
            }
        }
        return res;
    }
    template<bool unique = false>
    iterator kth(size_t k){
        assert(k <= (rt != nullptr ? (unique ? rt->sz : rt->sum) : 0));
        Node* cur = rt;
        while(true){
            if(cur->child[0] and k <= (unique ? cur->child[0]->sz : cur->child[0]->sum)){
                cur = cur->child[0];
            }else{
                if(cur->child[0]) k -= (unique ? cur->child[0]->sz : cur->child[0]->sum);
                if(k <= cur->cnt){
                    cur->splay();
                    rt = cur;
                    return iterator{cur};
                }
                k -= (unique ? 1 : cur->cnt);
                cur = cur->child[1];
            }
        }
    }
    static void destroy(Node* const node){
        if(!node) return;
        for(Node* const child: node->child){
            destroy(child);
        }
        delete node;
    }
    bool empty() const{
        return rt == nullptr;
    }
    size_t sum() const{
        return (rt == nullptr ? 0 : rt->sum);
    }
    size_t size() const{
        return (rt == nullptr ? 0 : rt->sz);
    }

    template<bool side = false>
    iterator begin(){
        return iterator{extremum<side>(rt)};
    }
    iterator rend(){
        return iterator{nullptr};
    }
    iterator end(){
        return iterator{nullptr};
    }
    iterator find(const T& key){
        Node* cur = rt;
        while(cur and key != cur->val){
            const auto nex = cur->child[key > cur->val];
            if(!nex) {
                cur->splay();
                rt = cur;
            }
            cur = nex;
        }
        return iterator{cur};
    }
    iterator lower_bound(const T& key){
        Node* cur = rt;
        Node* ret = nullptr;
        while(cur){
            if(cur->val > key){
                ret = cur;
                cur = cur->child[0];
            }else if(cur->val == key){
                ret = cur;
                break;
            }else{
                cur = cur->child[1];
            }
        }
        if(ret){
            ret->splay();
            rt = ret;
        }
        return iterator{ret};
    }
    Node* join(Node* const arg1, Node* const arg2){
        if(!arg1){
            arg2->parent = nullptr;
            return arg2;
        }
        arg1->parent = nullptr;
        Node* const mx = extremum<true>(arg1);
        mx->splay();
        rt = mx;
        assert(mx->child[1] == nullptr);
        mx->child[1] = arg2;
        mx->parent = nullptr;
        if(arg2) arg2->parent = mx;
        mx->maintain();
        return mx;
    }
    void erase(const iterator itr){
        if(!itr.node) return;
        Node* x = itr.node;
        x->splay();
        rt = x;
        rt = join(x->child[0], x->child[1]);
    }
    void extract(const iterator itr){
        if(!itr.node) return;
        if(itr.node->cnt == 1) erase(itr);
        else{
            itr.node->cnt--;
            itr.node->splay();
            rt = itr.node;
        }
    }
};
typedef pair<int, int> PII;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);
    SplayTree<int> st;
    int n;
    cin >> n;
    while(n--){
        int op;
        cin >> op;
        if(op == 1){
            int tv;
            cin >> tv;
            st.insert(tv);
        }else if(op == 2){
            int tv;
            cin >> tv;
            st.extract(st.find(tv));
        }else if(op == 3){
            int tv;
            cin >> tv;
            auto itr = st.find(tv);
            auto res = st.rank(tv);
            cout << res.second - (itr.node->cnt) + 1 << endl;
        }else if(op == 4){
            int tv;
            cin >> tv;
            auto itr = st.kth(tv);
            cout << itr.node->val << endl;
        }else if(op == 5){
            int tv;
            cin >> tv;
            auto itr = st.lower_bound(tv);
            if(itr == st.end()) itr = st.begin<true>();
            else --itr;
            cout << itr.node->val << endl;
        }else{
            int tv;
            cin >> tv;
            auto itr = st.lower_bound(tv);
            if(itr.node->val == tv) ++itr;
            cout << itr.node->val << endl;
        }
    }
    return 0;
}
```
### AVL树
```cpp
/**
 * @brief AVL 树
 * @author dianhsu
 * @date 2021/05/25
 * @ref https://zh.wikipedia.org/wiki/AVL树
 * */
#include <bits/stdc++.h>

template<class T>
struct AVLNode {
    T data;
    AVLNode<T> *leftChild;
    AVLNode<T> *rightChild;
    int height;

    AVLNode(T data): data(data), height(1), leftChild(nullptr), rightChild(nullptr) { }

    ~AVLNode() {
        delete leftChild;
        delete rightChild;
    }
};

template<class T>
class AVL {
public:
    AVL() {
        root = nullptr;
    }

    ~AVL() {
        delete root;
    }

    /**
     * @brief 将结点插入到AVL树中
     * @param val 需要插入的值
     * @note 如果发现这个树中已经有这个值存在了，就不会进行任何操作
     * */
    void insert(T val) {
        _insert(&root, val);
    }

    /**
     * @brief 检查结点是否在AVL树中
     * @param val 需要检查的值
     * */
    bool exist(T val) {
        auto ptr = &root;
        while (*ptr != nullptr) {
            if (val == (*ptr)->data) {
                return true;
            } else if (val < (*ptr)->data) {
                *ptr = (*ptr)->leftChild;
            } else {
                *ptr = (*ptr)->rightChild;
            }
        }
        return false;
    }

    /**
     * @brief 找到值为val的结点
     * @param val 目标值
     * @return 返回值为指向该结点的指针的地址
     */
    AVLNode<T> **find(T val) {
        auto ptr = &root;
        while ((*ptr) != nullptr) {
            if (val == (*ptr)->data) {
                break;
            } else if (val < (*ptr)->data) {
                *ptr = (*ptr)->leftChild;
            } else {
                *ptr = (*ptr)->rightChild;
            }
        }
        return ptr;
    }

    /**
     * @brief 删除结点
     * @note 首先找到结点，然后将结点旋转到叶子结点，然后回溯检查树的平衡性
     * @param val 需要删除的结点的值
     * @note 这个地方需要递归寻找该值的结点，因为需要回溯更新平衡树
     * */
    void remove(T val) {
        _remove(&root, val);
    }


private:
    void _remove(AVLNode<T> **ptr, T val) {
        if (*ptr == nullptr) {
            return;
        }
        if ((*ptr)->data == val) {
            _rotateNodeToLeaf(ptr);
        } else if ((*ptr)->data < val) {
            _remove(&((*ptr)->rightChild), val);
        } else {
            _remove(&((*ptr)->leftChild), val);
        }
        // 完了之后回溯，重新平衡二叉树
        _balance(ptr);
        _updateHeight(*ptr);
    }

    /**
     * @brief 将一个结点旋转到叶子结点
     * @param ptr 将要被旋转至叶子的结点的指针的地址
     * @note 旋转的时候，将当前结点旋转到高度比较小的一边。
     */
    void _rotateNodeToLeaf(AVLNode<T> **ptr) {
        // 当前结点已经是叶子结点了
        if ((*ptr)->leftChild == nullptr and (*ptr)->rightChild == nullptr) {
            *ptr = nullptr;
            return;
        }
        int leftHeight = (*ptr)->leftChild != nullptr ? (*ptr)->leftChild->height : 0;
        int rightHeight = (*ptr)->rightChild != nullptr ? (*ptr)->rightChild->height : 0;
        // 左边高度比较小，左旋
        if (leftHeight <= rightHeight) {
            _leftRotate(ptr);
            _rotateNodeToLeaf(&((*ptr)->leftChild));
        } else {
            // 右旋
            _rightRotate(ptr);
            _rotateNodeToLeaf(&((*ptr)->rightChild));
        }
        _balance(ptr);
        _updateHeight(*ptr);
    }

    /**
     * @brief 插入结点
     *
     * */
    void _insert(AVLNode<T> **ptr, T val) {
        if (*ptr == nullptr) {
            *ptr = new AVLNode<T>(val);
            return;
        }
        if (val < (*ptr)->data) {
            _insert(&((*ptr)->leftChild), val);
        } else if (val > (*ptr)->data) {
            _insert(&((*ptr)->rightChild), val);
        } else {
            // 如果当前平衡二叉树中已经存在这个结点了，不做任何处理
            return;
        }
        _balance(ptr);
        _updateHeight(*ptr);
    }

    /**
     * @brief 平衡结点
     *
     * */
    void _balance(AVLNode<T> **ptr) {
        if (*ptr == nullptr) return;
        int leftHeight = (*ptr)->leftChild != nullptr ? (*ptr)->leftChild->height : 0;
        int rightHeight = (*ptr)->rightChild != nullptr ? (*ptr)->rightChild->height : 0;
        if (abs(leftHeight - rightHeight) <= 1) return;

        if (leftHeight < rightHeight) {
            auto rightElement = (*ptr)->rightChild;
            int rightElementLeftHeight = rightElement->leftChild != nullptr ? rightElement->leftChild->height : 0;
            int rightElementRightHeight = rightElement->rightChild != nullptr ? rightElement->rightChild->height : 0;
            if (rightElementLeftHeight < rightElementRightHeight) {
                // RR
                _leftRotate(ptr);
            } else {
                // RL
                _rightRotate(&((*ptr)->rightChild));
                _leftRotate(ptr);
            }
        } else {
            auto leftElement = (*ptr)->leftChild;
            int leftElementLeftHeight = leftElement->leftChild != nullptr ? leftElement->leftChild->height : 0;
            int leftElementRightHeight = leftElement->rightChild != nullptr ? leftElement->rightChild->height : 0;
            if (leftElementLeftHeight > leftElementRightHeight) {
                // LL
                _rightRotate(ptr);
            } else {
                // LR
                _leftRotate(&((*ptr)->leftChild));
                _rightRotate(ptr);
            }
        }
    }

    /**
     * @brief 右旋
     *
     * */
    void _rightRotate(AVLNode<T> **ptr) {
        auto tmp = (*ptr)->leftChild;
        (*ptr)->leftChild = tmp->rightChild;
        tmp->rightChild = *ptr;
        _updateHeight(tmp);
        _updateHeight(*ptr);
        *ptr = tmp;
    }

    /**
     * @brief 左旋
     * */
    void _leftRotate(AVLNode<T> **ptr) {
        auto tmp = (*ptr)->rightChild;
        (*ptr)->rightChild = tmp->leftChild;
        tmp->leftChild = *ptr;
        _updateHeight(tmp);
        _updateHeight(*ptr);
        *ptr = tmp;
    }

    void _updateHeight(AVLNode<T> *ptr) {
        if (ptr == nullptr) return;
        int leftHeight = ptr->leftChild != nullptr ? ptr->leftChild->height : 0;
        int rightHeight = ptr->rightChild != nullptr ? ptr->rightChild->height : 0;
        ptr->height = std::max(leftHeight, rightHeight) + 1;
    }

    AVLNode<T> *root;
};

int main() {
    auto avl = new AVL<int>();
    int n = 20;
    std::random_device rd{};
    std::mt19937 gen{rd()};
    std::normal_distribution<> d{100, 100};
    std::uniform_int_distribution<int> u(0, INT_MAX >> 1);
    std::vector<int> vec;
    for (int i = 0; i < n; ++i) {
        vec.push_back((int) std::round(d(gen)));
        //vec.push_back(i);
    }
    for (auto it : vec) {
        avl->insert(it);
    }
    avl->remove(15);
    avl->remove(32);
    avl->remove(31);
    std::cout << *avl << std::endl;
    delete avl;
    return 0;
}
```
