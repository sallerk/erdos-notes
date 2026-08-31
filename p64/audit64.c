/* Independent audit of the #64 claim, using nauty's geng as the generator.
 *
 * CLAIM: every connected cubic bipartite graph on n <= 62 vertices contains a cycle of
 * length 2^k for some k >= 2.  The original search used a home-grown BFS-canonical
 * generator that performed NO isomorph rejection (nauty was unavailable then).  nauty
 * is available now, so this re-checks the same claim at every n it can reach, with a
 * completely different generator and a completely different cycle routine.
 *
 * For each graph read on stdin, reports whether it has a cycle of length exactly 4, 8
 * or 16.  A graph avoiding all three would be a survivor and is printed.
 *
 * Cycle detection is exact: depth-first enumeration of simple cycles through the
 * lowest-indexed vertex of each cycle, so each cycle is found once.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 64
static int n;
static unsigned long long adj[MAXN];
static int target, found;

static int decode_g6(const char *s, int *pn, unsigned long long *A)
{
    const unsigned char *p = (const unsigned char *)s;
    int nn = *p++ - 63;
    if (nn > MAXN) return 0;
    for (int i = 0; i < nn; i++) A[i] = 0ULL;
    int bit = 0, cur = 0;
    for (int j = 1; j < nn; j++)
        for (int i = 0; i < j; i++) {
            if (bit == 0) { cur = *p++ - 63; bit = 6; }
            bit--;
            if ((cur >> bit) & 1) { A[i] |= 1ULL << j; A[j] |= 1ULL << i; }
        }
    *pn = nn;
    return 1;
}

/* extend a path start -> ... -> cur of length len; look for a cycle of exactly target */
static void dfs(int start, int cur, unsigned long long used, int len)
{
    if (found) return;
    if (len == target) {
        if (adj[cur] >> start & 1ULL) found = 1;
        return;
    }
    unsigned long long cand = adj[cur] & ~used;
    /* only vertices above start, so each cycle is generated from its lowest vertex */
    cand &= ~((1ULL << (start + 1)) - 1);
    while (cand) {
        int w = __builtin_ctzll(cand);
        cand &= cand - 1;
        dfs(start, w, used | (1ULL << w), len + 1);
        if (found) return;
    }
}

static int has_cycle(int L)
{
    target = L; found = 0;
    for (int s = 0; s < n && !found; s++)
        dfs(s, s, 1ULL << s, 1);
    return found;
}

int main(int argc, char **argv)
{
    char line[512];
    long long tot = 0, surv = 0;
    long long h4 = 0, h8 = 0, h16 = 0;
    while (fgets(line, sizeof line, stdin)) {
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (!decode_g6(line, &n, adj)) continue;
        tot++;
        int c4 = has_cycle(4);
        if (c4) { h4++; continue; }
        int c8 = has_cycle(8);
        if (c8) { h8++; continue; }
        int c16 = (n >= 16) ? has_cycle(16) : 0;
        if (c16) { h16++; continue; }
        surv++;
        printf("SURVIVOR %s\n", line);
        fflush(stdout);
    }
    fprintf(stderr, "graphs=%lld  hasC4=%lld  hasC8(no C4)=%lld  hasC16(no C4,C8)=%lld  "
                    "SURVIVORS=%lld\n", tot, h4, h8, h16, surv);
    return 0;
}
