package com.algorand;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Optional;

import com.SandboxAccounts;
import com.algorand.algosdk.account.Account;
import com.algorand.algosdk.account.LogicSigAccount;
import com.algorand.algosdk.builder.transaction.ApplicationCallTransactionBuilder;
import com.algorand.algosdk.builder.transaction.MethodCallTransactionBuilder;
import com.algorand.algosdk.builder.transaction.PaymentTransactionBuilder;
import com.algorand.algosdk.crypto.Address;
import com.algorand.algosdk.transaction.AtomicTransactionComposer;
import com.algorand.algosdk.transaction.SignedTransaction;
import com.algorand.algosdk.transaction.Transaction;
import com.algorand.algosdk.transaction.TxGroup;
import com.algorand.algosdk.transaction.AtomicTransactionComposer.ExecuteResult;
import com.algorand.algosdk.util.Encoder;
import com.algorand.algosdk.v2.client.Utils;
import com.algorand.algosdk.v2.client.algod.GetApplicationByID;
import com.algorand.algosdk.v2.client.algod.TransactionParams;
import com.algorand.algosdk.v2.client.common.AlgodClient;
import com.algorand.algosdk.v2.client.common.Response;
import com.algorand.algosdk.v2.client.model.CompileResponse;
import com.algorand.algosdk.v2.client.model.DryrunRequest;
import com.algorand.algosdk.v2.client.model.DryrunResponse;
import com.algorand.algosdk.v2.client.model.TransactionParametersResponse;
import com.google.gson.Gson;

import org.apache.commons.lang3.StringUtils;

import com.algorand.algosdk.abi.Contract;
import com.algorand.algosdk.abi.Method;

public class main {

    public static Method getMethodByName(String name, Contract contract) throws Exception {
        Optional<Method> m = contract.methods.stream().filter(mt -> mt.name.equals(name)).findFirst();
        return m.orElseThrow(() -> new Exception("Method undefined: " + name));
    } 

    public static void main(String[] args) throws Exception {
        List<Account> accts = SandboxAccounts.getSandboxAccounts();

        AlgodClient client = new AlgodClient("http://localhost", 4001, "a".repeat(64));

        LogicSigAccount lsa = getLogic(client);


        // Read in contract json file
    	List<String> lines = Files.readAllLines(Paths.get("/home/ben/demo-abi/contract.json"), Charset.defaultCharset());
    	String jsonContract = StringUtils.join(lines, "");

    	// convert Json to contract
    	Contract contract = new Gson().fromJson(jsonContract, Contract.class);


	    // get transaction params
        Response<TransactionParametersResponse> sp = client.TransactionParams().execute();
        TransactionParametersResponse tsp = sp.body();

        List<Object> method_args = new ArrayList<Object>(); 
        method_args.add(1);
        method_args.add(1);

        // create methodCallParams by builder (or create by constructor) for add method
        MethodCallTransactionBuilder mtcb = MethodCallTransactionBuilder.Builder();
        mtcb.applicationId(50L);
        mtcb.sender(accts.get(0).getAddress().toString());
        mtcb.signer(accts.get(0).getTransactionSigner());
        mtcb.suggestedParams(tsp);
        mtcb.method(getMethodByName("add", contract));
        mtcb.methodArguments(method_args);

        AtomicTransactionComposer atc = new AtomicTransactionComposer();
        atc.addMethodCall(mtcb.build());

        ExecuteResult res = atc.execute(client, 2);

        //// Simple call to the `add` method, method_args can be any type but _must_
        //// match those in the method signature of the contract
        //atc.addMethodCall(methodCallParamsBuilderAddMethod.build());

        //// This method requires a `transaction` as its second argument. Construct the transaction and pass it in as an argument.
        //// The ATC will handle adding it to the group transaction and setting the reference in the application arguments.
        //Transaction ptxn = PaymentTransactionBuilder
        //        .Builder()
        //        .amount(10000)
        //        .suggestedParams(sp)
        //        .sender(acct.getAddress())
        //        .receiver(acct.getAddress())
        //        .build();

        //// create methodCallParams by builder (or create by constructor) for txntest method
        //MethodCallParams.Builder methodCallParamsBuilderTxnTest = new MethodCallParams.Builder();

        //// methodCallParams txtest: commons params
        //methodCallParamsBuilderTxnTest.setAppID(getAppId());
        //methodCallParamsBuilderTxnTest.setSender(acct.getAddress().toString());
        //methodCallParamsBuilderTxnTest.setSigner(signer);
        //methodCallParamsBuilderTxnTest.setSuggestedParams(sp);

        //// methodCallParams txntest: add method params
        //methodCallParamsBuilderTxnTest.setMethod(addmethod);
        //methodCallParamsBuilderTxnTest.methodArgs.add(10000);
        //methodCallParamsBuilderTxnTest.methodArgs.add(ptxn);
        //methodCallParamsBuilderTxnTest.methodArgs.add(1000);

        //atc.addMethodCall(methodCallParamsBuilderTxnTest.build());


	



        Transaction pay_txn = PaymentTransactionBuilder.Builder().amount(10000).suggestedParams(tsp)
                .sender(accts.get(0).getAddress()).receiver(lsa.getAddress()).build();

        List<Address> addrs = new ArrayList<>();
        addrs.add(accts.get(1).getAddress());

        List<Long> fassets = new ArrayList<>();
        //fassets.add(11L);

        List<Long> fapps = new ArrayList<>();
        //fapps.add(6L);

        Transaction app_txn = ApplicationCallTransactionBuilder.Builder().sender(accts.get(0).getAddress())
                .suggestedParams(tsp).applicationId(23L).foreignApps(fapps).foreignAssets(fassets).accounts(addrs).build();

        Transaction logic_txn = PaymentTransactionBuilder.Builder().amount(10000).suggestedParams(tsp)
                .sender(lsa.getAddress()).receiver(accts.get(0).getAddress()).build();

        // assign group ids
        Transaction[] txns = TxGroup.assignGroupID(pay_txn, app_txn, logic_txn);

        List<SignedTransaction> stxns = new ArrayList<>();
        stxns.add(accts.get(0).signTransaction(txns[0]));
        stxns.add(accts.get(0).signTransaction(txns[1]));
        stxns.add(lsa.signLogicSigTransaction(txns[2]));

        DryrunRequest drr = Utils.createDryrun(client, stxns, "", 0L, 0L);

        Response<DryrunResponse> resp = client.TealDryrun().request(drr).execute();
        
        DryrunResponse drResp = resp.body();

        System.out.println(Utils.appTrace(drResp.txns.get(1)));
        System.out.println(Utils.lsigTrace(drResp.txns.get(2)));

        //String fname = "java-drr.msgp";
        //FileOutputStream outfile = new FileOutputStream(fname);
        //outfile.write(Encoder.encodeToMsgPack(drr));
        //outfile.close();

        //System.out.println("Wrote to " + fname);
    }

    public static LogicSigAccount getLogic(AlgodClient client) throws Exception {

        BufferedReader br = new BufferedReader(new FileReader("/home/ben/sdk-extras/logic.teal"));
        StringBuilder sb = new StringBuilder();

        String line = br.readLine();
        while (line != null) {
            sb.append(line);
            sb.append(System.lineSeparator());
            line = br.readLine();
        }

        byte[] tealSrc = sb.toString().getBytes();

        Response<CompileResponse> compiled = client.TealCompile().source(tealSrc).execute();
        CompileResponse cr = compiled.body();

        byte[] program = Base64.getDecoder().decode(cr.result);

        LogicSigAccount lsa = new LogicSigAccount(program, null);

        return lsa;
    }
}