package route

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"opennamu/route/tool"
	"strconv"
)

func Api_bbs(call_arg []string) {
	db_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[0]), &db_set)

	other_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[1]), &other_set)

	db := tool.DB_connect(db_set)
	if db == nil {
		return
	}
	defer db.Close()

	var rows *sql.Rows
	if other_set["bbs_num"] == "" {
		var err error

		rows, err = db.Query(tool.DB_change(db_set, "select set_code, set_id from bbs_data where set_name = 'date' order by set_data desc limit 50"))
		if err != nil {
			return
		}
	} else {
		page, _ := strconv.Atoi(other_set["page"])
		num := 0
		if page*50 > 0 {
			num = page*50 - 50
		}

		stmt, err := db.Prepare(tool.DB_change(db_set, "select set_code, set_id from bbs_data where set_name = 'title' and set_id like ? order by set_code + 0 desc limit ?, 50"))
		if err != nil {
			return
		}
		defer stmt.Close()

		rows, err = stmt.Query(other_set["bbs_num"], num)
		if err != nil {
			return
		}
	}
	defer rows.Close()

	var data_list []map[string]string

	for rows.Next() {
		temp_data := make(map[string]string)

		var set_code string
		var set_id string

		err := rows.Scan(&set_code, &set_id)
		if err != nil {
			return
		}

		temp_data["set_code"] = set_code
		temp_data["set_id"] = set_id

		stmt, err := db.Prepare(tool.DB_change(db_set, "select set_name, set_data, set_code, set_id from bbs_data where set_code = ? and set_id = ?"))
		if err != nil {
			return
		}
		defer stmt.Close()

		rows, err := stmt.Query(set_code, set_id)
		if err != nil {
			return
		}
		defer rows.Close()

		for rows.Next() {
			var set_name string
			var set_data string

			err := rows.Scan(&set_name, &set_data, &set_code, &set_id)
			if err != nil {
				return
			}

			temp_data[set_name] = set_data
		}

		data_list = append(data_list, temp_data)
	}

	if len(data_list) == 0 {
		fmt.Print("{}")
	} else {
		json_data, _ := json.Marshal(data_list)
		fmt.Print(string(json_data))
	}
}
