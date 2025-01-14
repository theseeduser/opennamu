from .tool.func import *

from .go_api_search import api_search

def main_search_deep(db_set, name = 'Test', search_type = 'title', num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if name == '':
            return redirect()

        sql_num = (num * 50 - 50) if num * 50 > 0 else 0

        if flask.request.method == 'POST':
            if search_type == 'title':
                return redirect('/search_page/1/' + url_pas(flask.request.form.get('search', 'test')))
            else:
                return redirect('/search_data_page/1/' + url_pas(flask.request.form.get('search', 'test')))
        else:
            div = '''
                <form method="post">
                    <input class="opennamu_width_200" name="search" value="''' + html.escape(name) + '''">
                    <button type="submit">''' + load_lang('search') + '''</button>
                </form>
                <hr class="main_hr">
            '''

            if search_type == 'title':
                div += '<a href="/search_data_page/1/' + url_pas(name) + '">(' + load_lang('search_document_data') + ')</a>'
            else:
                div += '<a href="/search_page/1/' + url_pas(name) + '">(' + load_lang('search_document_name') + ')</a>'

            name_new = ''
            if re.search(r'^분류:', name):
                name_new = re.sub(r"^분류:", 'category:', name)
            elif re.search(r"^사용자:", name):
                name_new = re.sub(r"^사용자:", 'user:', name)
            elif re.search(r"^파일:", name):
                name_new = re.sub(r"^파일:", 'file:', name)

            if name_new != '':
                div += ' <a href="/search_page/1/' + url_pas(name_new) + '">(' + name_new + ')</a>'

            curs.execute(db_change("select title from data where title = ? collate nocase"), [name])
            link_id = '' if curs.fetchall() else 'class="opennamu_not_exist_link"'

            div += '''
                <ul class="opennamu_ul">
                    <li>
                        <a ''' + link_id + ' href="/w/' + url_pas(name) + '">' + html.escape(name) + '''</a>
                    </li>
                </ul>
                <ul class="opennamu_ul">
            '''

            all_list = json.loads(api_search(db_set, name, search_type, num).data)
            for data in all_list:
                div += '<li><a href="/w/' + url_pas(data) + '">' + data + '</a></li>'

            div += '</ul>'
            
            if search_type == 'title':
                div += get_next_page_bottom('/search_page/{}/' + url_pas(name), num, all_list)
            else:
                div += get_next_page_bottom('/search_data_page/{}/' + url_pas(name), num, all_list)

            return easy_minify(flask.render_template(skin_check(),
                imp = [name, wiki_set(), wiki_custom(), wiki_css(['(' + load_lang('search') + ')', 0])],
                data = div,
                menu = 0
            ))