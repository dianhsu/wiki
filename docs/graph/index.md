--- 
comments: true
---
## Graph

### Disjoint Union
> 能Copy的时候，就不用手搓了

```cpp
class DSU{
public:
    explicit DSU(int size_): sz(size_), fa(size_, 0), cnt(size_, 1) {
        iota(fa.begin(), fa.end(), 0);
    }
    int tf(int x){
        return x == fa[x] ? x : fa[x] = tf(fa[x]);
    }
    bool mg(int x, int y){
        int tx = tf(x), ty = tf(y);
        if(tx != ty){
            if(cnt[tx] >= cnt[ty]){ // 启发式合并
                fa[ty] = tx;
                cnt[tx] += cnt[ty];
            }else{
                fa[tx] = ty;
                cnt[ty] += cnt[tx];
            }
            return true;
        }
        return false;
    }
    pair<int, int> operator [] (const int idx) {
        return {tf(idx), cnt[tf(idx)]};
    }
    int size(){
        return sz;
    }
private:
    int sz;
    vector<int> fa, cnt;
};

```

### Network Flow

#### 最大流(Dinic)
```cpp
template<typename cap_t>
class Dinic{
public:
    explicit Dinic(int n): node_cnt(n), g(n){}
    int add_edge(int from, int to, cap_t cap){
        int m = int(pos.size());
        pos.emplace_back(from, int(g[from].size()));
        int from_id = int(g[from].size());
        int to_id = int(g[to].size());
        if(from == to) to_id++;
        g[from].push_back(PrivateEdge{to, to_id, cap});
        g[to].push_back(PrivateEdge{from, from_id, 0});
        return m;
    }
    struct Edge{
        int from, to;
        cap_t cap, flow;
    };
    Edge getEdge(int idx){
        auto _e = g[pos[idx].first][pos[idx].second];
        auto _re = g[_e.to][_e.rev];
        return Edge{pos[idx].first, _e.to, _e.cap + _re.cap, _re.cap};
    }
    std::vector<Edge> getEdges(){
        std::vector<Edge> result;
        for(int i = 0; i < pos.size(); ++i){
            result.push_back(getEdge(i));
        }
        return result;
    }
    cap_t flow(int st, int ed){
        return flow(st, ed, std::numeric_limits<cap_t>::max());
    }
    cap_t flow(int st, int ed, cap_t flow_limit){
        std::vector<int> level(node_cnt);
        std::queue<int> que;
        auto&& bfs = [&](){
            std::fill(level.begin(), level.end(), -1);
            level[st] = 0;
            while(!que.empty()){
                que.pop();
            }
            que.push(st);
            while(!que.empty()){
                int v = que.front();
                que.pop();
                for(PrivateEdge& e: g[v]){
                    if(e.cap == 0 or level[e.to] >= 0) continue;
                    level[e.to] = level[v] + 1;
                    if(e.to == ed) continue;
                    que.push(e.to);
                }
            }
        };
        auto&& dfs = [&](auto&& self, int v, cap_t up){
            if(v == st) return up;
            cap_t res = 0;
            int level_v = level[v];
            for(int idx = 0; idx < int(g[v].size()); ++idx){
                PrivateEdge& edge = g[v][idx];
                if(level_v <= level[edge.to] or g[edge.to][edge.rev].cap == 0) continue;
                cap_t delta = self(self, edge.to, std::min(up - res, g[edge.to][edge.rev].cap));
                if(delta <= 0) continue;
                g[v][idx].cap += delta;
                g[edge.to][edge.rev].cap -= delta;
                res += delta;
                if(res == up) return res;
            }
            level[v] = node_cnt;
            return res;
        };
        cap_t ans = 0;
        while (ans < flow_limit){
            bfs();
            if(level[ed] == -1) break;
            cap_t delta = dfs(dfs, ed, flow_limit - ans);
            if(!delta) break;
            ans += delta;
        }
        return ans;
    }
private:
    struct PrivateEdge{
        int to, rev;
        cap_t cap;
    };
    int node_cnt;
    std::vector<std::pair<int, int>> pos;
    std::vector<std::vector<PrivateEdge>> g;
};
```

#### 最小费用流(Dinic)
> Atcoder

```cpp
template <class Cap, class Cost> struct mcf_graph {
public:
    mcf_graph() {}
    explicit mcf_graph(int n) : _n(n) {}

    int add_edge(int from, int to, Cap cap, Cost cost) {
        assert(0 <= from && from < _n);
        assert(0 <= to && to < _n);
        assert(0 <= cap);
        assert(0 <= cost);
        int m = int(_edges.size());
        _edges.push_back({from, to, cap, 0, cost});
        return m;
    }

    struct edge {
        int from, to;
        Cap cap, flow;
        Cost cost;
    };

    template <class E> struct csr {
        std::vector<int> start;
        std::vector<E> elist;
        explicit csr(int n, const std::vector<std::pair<int, E>>& edges)
            : start(n + 1), elist(edges.size()) {
            for (auto e : edges) {
                start[e.first + 1]++;
            }
            for (int i = 1; i <= n; i++) {
                start[i] += start[i - 1];
            }
            auto counter = start;
            for (auto e : edges) {
                elist[counter[e.first]++] = e.second;
            }
        }
    };

    edge get_edge(int i) {
        int m = int(_edges.size());
        assert(0 <= i && i < m);
        return _edges[i];
    }
    std::vector<edge> edges() { return _edges; }

    std::pair<Cap, Cost> flow(int s, int t) {
        return flow(s, t, std::numeric_limits<Cap>::max());
    }
    std::pair<Cap, Cost> flow(int s, int t, Cap flow_limit) {
        return slope(s, t, flow_limit).back();
    }
    std::vector<std::pair<Cap, Cost>> slope(int s, int t) {
        return slope(s, t, std::numeric_limits<Cap>::max());
    }
    std::vector<std::pair<Cap, Cost>> slope(int s, int t, Cap flow_limit) {
        assert(0 <= s && s < _n);
        assert(0 <= t && t < _n);
        assert(s != t);

        int m = int(_edges.size());
        std::vector<int> edge_idx(m);

        auto g = [&]() {
            std::vector<int> degree(_n), redge_idx(m);
            std::vector<std::pair<int, _edge>> elist;
            elist.reserve(2 * m);
            for (int i = 0; i < m; i++) {
                auto e = _edges[i];
                edge_idx[i] = degree[e.from]++;
                redge_idx[i] = degree[e.to]++;
                elist.push_back({e.from, {e.to, -1, e.cap - e.flow, e.cost}});
                elist.push_back({e.to, {e.from, -1, e.flow, -e.cost}});
            }
            auto _g = csr<_edge>(_n, elist);
            for (int i = 0; i < m; i++) {
                auto e = _edges[i];
                edge_idx[i] += _g.start[e.from];
                redge_idx[i] += _g.start[e.to];
                _g.elist[edge_idx[i]].rev = redge_idx[i];
                _g.elist[redge_idx[i]].rev = edge_idx[i];
            }
            return _g;
        }();

        auto result = slope(g, s, t, flow_limit);

        for (int i = 0; i < m; i++) {
            auto e = g.elist[edge_idx[i]];
            _edges[i].flow = _edges[i].cap - e.cap;
        }

        return result;
    }

private:
    int _n;
    std::vector<edge> _edges;

    // inside edge
    struct _edge {
        int to, rev;
        Cap cap;
        Cost cost;
    };

    std::vector<std::pair<Cap, Cost>> slope(csr<_edge>& g,
        int s,
        int t,
        Cap flow_limit) {
        // variants (C = maxcost):
        // -(n-1)C <= dual[s] <= dual[i] <= dual[t] = 0
        // reduced cost (= e.cost + dual[e.from] - dual[e.to]) >= 0 for all edge

        // dual_dist[i] = (dual[i], dist[i])
        std::vector<std::pair<Cost, Cost>> dual_dist(_n);
        std::vector<int> prev_e(_n);
        std::vector<bool> vis(_n);
        struct Q {
            Cost key;
            int to;
            bool operator<(Q r) const { return key > r.key; }
        };
        std::vector<int> que_min;
        std::vector<Q> que;
        auto dual_ref = [&]() {
            for (int i = 0; i < _n; i++) {
                dual_dist[i].second = std::numeric_limits<Cost>::max();
            }
            std::fill(vis.begin(), vis.end(), false);
            que_min.clear();
            que.clear();

            // que[0..heap_r) was heapified
            size_t heap_r = 0;

            dual_dist[s].second = 0;
            que_min.push_back(s);
            while (!que_min.empty() || !que.empty()) {
                int v;
                if (!que_min.empty()) {
                    v = que_min.back();
                    que_min.pop_back();
                } else {
                    while (heap_r < que.size()) {
                        heap_r++;
                        std::push_heap(que.begin(), que.begin() + heap_r);
                    }
                    v = que.front().to;
                    std::pop_heap(que.begin(), que.end());
                    que.pop_back();
                    heap_r--;
                }
                if (vis[v]) continue;
                vis[v] = true;
                if (v == t) break;
                // dist[v] = shortest(s, v) + dual[s] - dual[v]
                // dist[v] >= 0 (all reduced cost are positive)
                // dist[v] <= (n-1)C
                Cost dual_v = dual_dist[v].first, dist_v = dual_dist[v].second;
                for (int i = g.start[v]; i < g.start[v + 1]; i++) {
                    auto e = g.elist[i];
                    if (!e.cap) continue;
                    // |-dual[e.to] + dual[v]| <= (n-1)C
                    // cost <= C - -(n-1)C + 0 = nC
                    Cost cost = e.cost - dual_dist[e.to].first + dual_v;
                    if (dual_dist[e.to].second - dist_v > cost) {
                        Cost dist_to = dist_v + cost;
                        dual_dist[e.to].second = dist_to;
                        prev_e[e.to] = e.rev;
                        if (dist_to == dist_v) {
                            que_min.push_back(e.to);
                        } else {
                            que.push_back(Q{dist_to, e.to});
                        }
                    }
                }
            }
            if (!vis[t]) {
                return false;
            }

            for (int v = 0; v < _n; v++) {
                if (!vis[v]) continue;
                // dual[v] = dual[v] - dist[t] + dist[v]
                //         = dual[v] - (shortest(s, t) + dual[s] - dual[t]) +
                //         (shortest(s, v) + dual[s] - dual[v]) = - shortest(s,
                //         t) + dual[t] + shortest(s, v) = shortest(s, v) -
                //         shortest(s, t) >= 0 - (n-1)C
                dual_dist[v].first -= dual_dist[t].second - dual_dist[v].second;
            }
            return true;
        };
        Cap flow = 0;
        Cost cost = 0, prev_cost_per_flow = -1;
        std::vector<std::pair<Cap, Cost>> result = {{Cap(0), Cost(0)}};
        while (flow < flow_limit) {
            if (!dual_ref()) break;
            Cap c = flow_limit - flow;
            for (int v = t; v != s; v = g.elist[prev_e[v]].to) {
                c = std::min(c, g.elist[g.elist[prev_e[v]].rev].cap);
            }
            for (int v = t; v != s; v = g.elist[prev_e[v]].to) {
                auto& e = g.elist[prev_e[v]];
                e.cap += c;
                g.elist[e.rev].cap -= c;
            }
            Cost d = -dual_dist[s].first;
            flow += c;
            cost += c * d;
            if (prev_cost_per_flow == d) {
                result.pop_back();
            }
            result.push_back({flow, cost});
            prev_cost_per_flow = d;
        }
        return result;
    }
};
```
### Tarjan
> 解决关键边和关键点很好用

```cpp
const int maxn = 100100;
int dfn[maxn], low[maxn];
int tim;
int vis[maxn];
int sd[maxn];
std::stack<int> st;
vector<vector<int>> g;
void tarjan(int cur){
    dfn[cur] = low[cur] = ++tim; 
    vis[cur] = 1;
    st.push(cur);
    for(auto& nex: g[cur]){
        if(!dfn[nex]){
            tarjan(nex);
            low[cur] = min(low[cur], low[nex]);
        }else if(vis[nex]){
            low[cur] = min(low[cur], dfn[nex]);
        }
    }
    if(dfn[cur] == low[cur]){
        while(!st.empty()){
            auto pos = st.top();
            st.pop();
            vis[pos] = 0;
            sd[pos] = cur;
            if(pos == cur) break;
        }
    }
}

```
