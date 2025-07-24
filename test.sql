SELECT string_split(replace(replace(replace(options_approved, '[', ''), ']', ''), \"'\", ''), ', ') AS options_list FROM postures_sub_postures;
