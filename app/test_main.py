from app.helpers import Side, ActionType, BuildAndDestroyType
from app.map import Map, create_new_map_from_old_map_and_actions
from app.models import GameResp, GameActionsResp

init_map = Map(width=11, height=11, canvas=None, start_queue=False)

init_map.init_map_but_not_render(
    data=GameResp(
        field=GameResp.Field(
            castle_coeff=10,
            wall_coeff=1,
            territory_coeff=1,
            width=11,
            height=11,
            ponds=[
                GameResp.Field.PondResp(x=0, y=0)
            ],
            castles=[GameResp.Field.CastleResp(x=7, y=7)],
            craftsmen=[
                GameResp.Field.CraftsMenResp(x=1, y=1, side=Side.A, id="1"),
                GameResp.Field.CraftsMenResp(x=2, y=2, side=Side.A, id="2"),
                GameResp.Field.CraftsMenResp(x=3, y=3, side=Side.A, id="3"),
                GameResp.Field.CraftsMenResp(x=4, y=4, side=Side.B, id="4"),
                GameResp.Field.CraftsMenResp(x=5, y=5, side=Side.B, id="5"),
                GameResp.Field.CraftsMenResp(x=6, y=6, side=Side.B, id="6")
            ]
        )
    )
)

print(init_map.calculate_point())
new_map = create_new_map_from_old_map_and_actions(
    old_map=init_map,
    list_actions=GameActionsResp(
        actions=[
            GameActionsResp.ChildAction(
                action=ActionType.BUILD,
                action_param=BuildAndDestroyType.LEFT,
                craftsman_id="1"
            ),
            GameActionsResp.ChildAction(
                action=ActionType.BUILD,
                action_param=BuildAndDestroyType.LEFT,
                craftsman_id="2"
            ),
        ]
    )
)
print(new_map.calculate_point())
