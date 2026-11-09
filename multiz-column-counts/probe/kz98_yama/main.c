/* Harness: read K M then M lines of K chars (columns of A), L N then N lines
 * of L chars (columns of B). Full band. Print the output columns, one per line,
 * A part then B part. Also print gop table once with -g. */
#include "util.h"
#include "mz_scores.h"
#include "mz_yama.h"
int main(int argc, char **argv) {
    int K, M, L, N, i, OM, *LB, *RB;
    uchar **A, **B, **AL;
    char buf[1024];
    init_scores70();
    if (argc > 1) {
        for (i = 0; i < 16; i++) printf("%d ", gop[i]);
        printf("\n%d %d %d %d %d\n", gap_open, gap_extend, ss['A']['-'], ss['-']['-'], ss['A']['N']);
        return 0;
    }
    while (scanf("%d %d", &K, &M) == 2) {
        A = (uchar **)ckalloc(M*sizeof(uchar *)) - 1;
        for (i = 1; i <= M; i++) { scanf("%s", buf); A[i] = (uchar *)copy_string(buf); }
        scanf("%d %d", &L, &N);
        B = (uchar **)ckalloc(N*sizeof(uchar *)) - 1;
        for (i = 1; i <= N; i++) { scanf("%s", buf); B[i] = (uchar *)copy_string(buf); }
        LB = ckalloc((M+1)*sizeof(int)); RB = ckalloc((M+1)*sizeof(int));
        for (i = 0; i <= M; i++) { LB[i] = 0; RB[i] = N; }
        yama(A, K, M, B, L, N, LB, RB, &AL, &OM);
        printf("%d\n", OM);
        for (i = 1; i <= OM; i++) printf("%.*s\n", K+L, AL[i]);
        fflush(stdout);
    }
    return 0;
}
