(function(global){
    // 存放私有變數
    var _private = {};

    _private.crypto = window.crypto && window.crypto.getRandomValues;

    _private.rng = function(nums, base) {
        var arr, i;
        if(_private.crypto){
            arr = new Uint32Array(nums);
            window.crypto.getRandomValues(arr);
        } else {
            arr = [];
            i = nums;
            while(i--){
                arr.push(Math.floor(Math.random() * Math.pow(2,32)) >>> 0);
            }
        }
        if(base){
            while(nums--){
                arr[nums] = arr[nums].toString(base);
            }
        }
        return arr;
    };

    function Diffie(options){
        options = options || {};
        this.secret = options.key || this.genSecret();
        if(options.common){
            var _base = options.common.base;
            var _modulus = options.common.modulus;
            this.common = {
                base: (_base instanceof BI ? _base : new BI(_base)),
                modulus: (_modulus instanceof BI ? _modulus : new BI(_modulus))
            };
            this.genShared();
        }
        return this;
    }

    Diffie.config = {
        bits: {
            modulus: 2048,
            base: 224,
            secret: 256
        }
    };

    Diffie.prototype.genSecret = function(){
        var blocks, blockArr;
        blocks = Math.ceil(Diffie.config.bits.secret / 32);
        blockArr = _private.rng(blocks, 16);
        this.secret = new BI(blockArr.join(''), 16);
        return this.secret;
    };

    Diffie.prototype.setCommon = function(base, modulus){
        Diffie.config.bits.modulus = modulus;
        Diffie.config.bits.base = base;

        this.common = {
            base: (base instanceof BI ? base : new BI(base)),
            modulus: (modulus instanceof BI ? modulus : new BI(modulus))
        };
        this.genShared();
    };

    Diffie.prototype.genShared = function(){
        this.shared = this.common.base.powmod(this.secret, this.common.modulus);
        return this.shared;
    };

    Diffie.prototype.updateShared = function(sharedKey){
        return sharedKey.powmod(this.secret, this.common.modulus);
    };

    // 將 Diffie 函式庫暴露給全域變數
    global.MyDiffie = Diffie;

    /*
    * Diffie.generateModulus - 依據 Diffie.config.bits.modulus 隨機產生一個大質數作為 modulus
    * @return {BI} - 產生的 modulus (大質數)
    */
    Diffie.generateModulus = function(){
        var bitLength = Diffie.config.bits.modulus;
        // 以 32 位元為一個區塊所需的數量
        var blocks = Math.ceil(bitLength / 32);
        // 利用 _private.rng 產生相對應的隨機數 (以16 進位表示)
        var blockArr = _private.rng(blocks, 16);
        var candidateHex = blockArr.join('');
        var candidate = new BI(candidateHex, 16);

        // 強制 candidate 至少具有 bitLength - 1 個位元
        var min = new BI("1",10).shiftLeft(bitLength - 1);
        if(candidate.compareTo(min) < 0){
            candidate = candidate.add(min);
        }
        // 保證為奇數，因偶數不可能為質數（除了 2 之外）
        if(candidate.modInt(2) === 0) {
            candidate = candidate.add(new BI("1",10));
        }
        // 驗證 candidate 是否為質數，若不是則不斷加2 (維持奇數) ，直到通過試驗 (這裡使用 isProbablePrime 判斷，設定 10 次檢驗)
        while(!candidate.isProbablePrime(10)){
            candidate = candidate.add(new BI("2",10));
        }
        return candidate;
    };

    // 使用範例:
    // var modulus = Diffie.generateModulus();
    // console.log("Generated modulus (hex):", modulus.toString(16));

})(window);