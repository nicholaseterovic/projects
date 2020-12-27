window.dapp  = Object.assign({}, window.dapp, {
    tabulator:{
        selectableCheck:function (row){
            return true;
            var irow = row.getPosition(true);
            var table = row.getTable();
            var nrows = table.getRows().length;
            var ilast = irow==nrows;
            return ilast;
        },
        tooltip:function(cell){
            return "hi";
        },
        rowFormatter:function(row, data){
            row.getElement().addClass("success");
        },
    }
});