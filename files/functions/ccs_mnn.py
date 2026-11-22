import files.functions.CCS_CoreNetWork as C3

class CCScore(C3.CCScore):
    def __init__(self, chess, difficulty=400, ai_player=2, c_puct=1.0,
                 temperature=0.1, n_threads=4, sigma=0.001, username=None, opp_weight=0.3):
        super().__init__(
            chess=chess,
            difficulty=difficulty,
            ai_player=ai_player,
            c_puct=c_puct,
            temperature=temperature,
            n_threads=n_threads,
            sigma=sigma,
            username=username,
            opp_weight=opp_weight
        )
        self.human_player = 1