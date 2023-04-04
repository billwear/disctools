#!/usr/bin/python3
# json2dcmd
# stdin JSON ->> dicourse markdown ->> stdout Discourse markdown
#
# requirements (progressive)
# - take JSON input and output a discourse markdown table
#
# step 3: interpret input as JSON
#
import sys, json

# pull in the json stream from stdin
data = json.load(sys.stdin)

# loop through the json lines
for d in data:

    # loop through the line dictionary
    for x in d:

        # if this line is a table
        if x == "table":  # create a list and strings for the table rows
            dc_table = []
            row_str = "|"
            sep_row_str = "|"

            # isolate the table itself
            table = d["table"]

            # capture the table name
            name = table["name"]

            # transform table name to a level 2 heading
            section_anchor_id = "heading--"
            section_anchor_id += (
                name.replace(" ", "-")
                .replace("(", "-")
                .replace(")", "-")
                .replace(".", "-")
            )
            section_anchor = "#" + section_anchor_id
            section_head = (
                '<a href="'
                + section_anchor
                + '"><h2 id="'
                + section_anchor_id
                + "></a>\n\n"
            )

            # add the section heading to the output
            dc_table.append(section_head)

            # capture the table rows
            rows = table["rows"]

            # build the heading row (all rows assume same headings)
            # && the separator row
            for head in rows[0]:
                row_str += head + "|"
                sep_row_str += "-----|"

            # add the heading rows to the output table
            dc_table.append(row_str + "\n")
            dc_table.append(sep_row_str + "\n")

            # build the data rows & add to the output table
            for row in rows:
                row_str = "|"
                for head, value in row.items():
                    row_str += value + "|"
                row_str += "\n"
                dc_table.append(row_str)

            # go ahead and print this to stdout
            for row in dc_table:
                print(row, end="")

            # print a newline to separate this from other output
            print(" ")
