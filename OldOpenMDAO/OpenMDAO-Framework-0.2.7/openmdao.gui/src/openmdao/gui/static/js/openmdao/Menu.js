
var openmdao = (typeof openmdao === "undefined" || !openmdao ) ? {} : openmdao ;

openmdao.Menu = function(id, json) {
    /***********************************************************************
     *  private
     ***********************************************************************/
    var self = this,
        elm = jQuery("#"+id);

    /** build menus from JSON data structure */
    function buildMenus(menus) {
        // generate HTML for the menus
        var i = 0,
            html = "<ul>";
        for (i = 0; i < menus.length; i++) {
            html += getMenuHTML(menus[i]);
        }
        html += "</ul>";
        elm.html(html);

        // Add indicators and hovers to submenu parents.
        // The slides look pretty, but cause problems for Selenium,
        // so they're disabled when testing.
        elm.find("li").each(function() {
            var header = jQuery(this).children(":first"),
                menu = jQuery(this).find("ul"),
                showMenu = function() {
                    if (typeof openmdao_test_mode === "undefined") {
                        menu.stop(true, true).slideDown();
                    }
                },
                hideMenu = function() {
                    if (typeof openmdao_test_mode === "undefined") {
                        menu.stop(true, true).slideUp();
                    }
                },
                settings = {
                    timeout: 500,
                    over: showMenu,
                    out: hideMenu
                };

            // When testing, toggle this menu and hide all the others on click.
            header.click(function() {
                if (typeof openmdao_test_mode !== "undefined") {
                    menu.toggle();
                    header.parent().siblings().find("ul").hide();
                }
            });

            if (menu.length > 0) {
                jQuery("<span>").text("^").appendTo(header);
                jQuery(this).hoverIntent( settings );
                menu.find("li").click(function() { menu.toggle(); });
            }
        });
    }

    /** recursively build HTML for JSON nested menu structure */
    function getMenuHTML(menu) {
        var menuHTML = '<li><a ';
        if (menu.hasOwnProperty('url')) {
            menuHTML += 'href="'+menu.url+'" ';
        }
        if (menu.hasOwnProperty('onclick')) {
            menuHTML += 'onclick="'+menu.onclick+'" ';
        }
        if (menu.hasOwnProperty('id')) {
            menuHTML += 'id="'+menu.id+'" ';
        }
        menuHTML += '>'+menu.text+'</a>';

        if (menu.hasOwnProperty('items')) {
            var i = 0;
            menuHTML += "<ul>";
            for (i = 0; i < menu.items.length; i++) {
                menuHTML += getMenuHTML(menu.items[i]);
            }
            menuHTML += "</ul>";
        }

        menuHTML += '</li>';
        return menuHTML;
    }

    /***********************************************************************
     *  privileged
     ***********************************************************************/

    /** rebuild menus from given JSON data */
    this.updateFromJSON = function(json) {
        buildMenus(json);
    };

    /** rebuild menus from JSON at given url */
    this.updateFromURL = function(url) {
        jQuery.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            success: buildMenus,
            error: function(x,y,z) {
                debug.info("Error getting Menu data:",x,y,z);
            }
        });
    };

    buildMenus(json);
};
